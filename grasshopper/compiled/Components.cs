using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Reflection;
using System.Text.Json;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;

namespace PlugInSolar {
public class SolarData : GH_Goo<string> {
    public SolarData() { Value="{}"; }
    public SolarData(string json) { Value=json; }
    public override bool IsValid => !string.IsNullOrEmpty(Value);
    public override string TypeName => "Solar Data";
    public override string TypeDescription => "Time-indexed Plug-In Solar calculation data";
    public override IGH_Goo Duplicate() => new SolarData(Value);
    public override string ToString() => "Plug-In Solar data";
    public override bool Write(GH_IO.Serialization.GH_IWriter writer) {writer.SetString("json",Value);return true;}
    public override bool Read(GH_IO.Serialization.GH_IReader reader) {Value=reader.GetString("json");return true;}
}
static class Assets {
    public static JsonElement[] Specs = Load();
    static JsonElement[] Load() {using(var s=Assembly.GetExecutingAssembly().GetManifestResourceStream("PlugInSolar.components.json")) return JsonSerializer.Deserialize<JsonElement[]>(s);}
    public static JsonElement Spec(string id)=>Specs.First(s=>s.GetProperty("id").GetString()==id);
    public static Bitmap Icon(string id) {using(var s=Assembly.GetExecutingAssembly().GetManifestResourceStream("PlugInSolar.icons."+id+"-24.png")) using(var b=new Bitmap(s)) return new Bitmap(b);}
}
public class Info : GH_AssemblyInfo {
    public override string Name=>"Plug-In Solar";
    public override string Description=>"pvlib solar modelling components for Rhino 8";
    public override Guid Id=>new Guid("ba3e852e-04f2-46a3-933b-fef28736aeee");
    public override Bitmap Icon=>Assets.Icon("plug_in_solar");
    public override string AuthorName=>"Plug-In Solar";
    public override string AuthorContact=>"";
}
public abstract class SolarComponent : GH_Component {
    readonly string id;
    string cachedRequest, cachedResponse;
    protected SolarComponent(string op):base(Assets.Spec(op).GetProperty("name").GetString(),Assets.Spec(op).GetProperty("nickname").GetString(),Assets.Spec(op).GetProperty("description").GetString(),"Plug-In Solar",Assets.Spec(op).GetProperty("subcategory").GetString()) {id=op;}
    // Registration is called by GH_Component's constructor, before our fields are set.
    JsonElement Spec=>Assets.Spec(id ?? Operation);
    protected abstract string Operation {get;}
    protected override Bitmap Icon=>Assets.Icon(Operation);
    static Dictionary<string,double> defaults=new Dictionary<string,double> {{"altitude_m",0},{"step_minutes",60},{"north_deg",0},{"albedo",0.2},{"dc_capacity_w",800},{"ac_limit_w",800},{"air_temp_c",20},{"wind_m_s",1},{"gamma_pdc",-0.004},{"losses_pct",14},{"step_hours",1}};
    protected override void RegisterInputParams(GH_InputParamManager p) {
        foreach(var port in Spec.GetProperty("inputs").EnumerateArray()) {
            string n=port.GetProperty("name").GetString(),h=port.GetProperty("hint").GetString();
            if(n=="project_root")continue;
            string tip=n.Replace('_',' ');
            if(h=="float") {if(defaults.TryGetValue(n,out double val))p.AddNumberParameter(n,n,tip,GH_ParamAccess.item,val);else p.AddNumberParameter(n,n,tip,GH_ParamAccess.item);}
            else if(h=="str")p.AddTextParameter(n,n,tip,GH_ParamAccess.item);
            else if(h=="Vector3d")p.AddVectorParameter(n,n,tip,GH_ParamAccess.item);
            else p.AddGenericParameter(n,n,tip,GH_ParamAccess.item);
        }
    }
    protected override void RegisterOutputParams(GH_OutputParamManager p) {
        foreach(var port in Spec.GetProperty("outputs").EnumerateArray()) {
            string n=port.GetString();
            if(new[]{"site","weather","solar","poa","power"}.Contains(n))p.AddGenericParameter(n,n,"Connect to the next Plug-In Solar component",GH_ParamAccess.item);
            else if(n=="timestamps")p.AddTextParameter(n,n,"Timezone-aware timestamps",GH_ParamAccess.list);
            else p.AddNumberParameter(n,n,n.Replace('_',' '),new[]{"tilt_deg","total_kwh"}.Contains(n)||(n=="azimuth_deg"&&Operation=="panel_orientation")?GH_ParamAccess.item:GH_ParamAccess.list);
        }
    }
    protected override void SolveInstance(IGH_DataAccess da) {
        try {
            var inputs=new Dictionary<string,object>();int i=0;
            foreach(var port in Spec.GetProperty("inputs").EnumerateArray()) {
                string n=port.GetProperty("name").GetString(),h=port.GetProperty("hint").GetString();
                if(n=="project_root")continue;
                if(h=="float") {double v=0;if(!da.GetData(i++,ref v))return;inputs[n]=v;}
                else if(h=="str") {string v="";if(!da.GetData(i++,ref v))return;inputs[n]=v;}
                else if(h=="Vector3d") {Vector3d v=Vector3d.Unset;if(!da.GetData(i++,ref v))return;inputs[n]=new[]{v.X,v.Y,v.Z};}
                else {IGH_Goo v=null;if(!da.GetData(i++,ref v))return;var d=v as SolarData;if(d==null && v is GH_ObjectWrapper w)d=w.Value as SolarData;if(d==null)throw new ArgumentException(n+" requires a Plug-In Solar data output.");inputs[n]=JsonSerializer.Deserialize<JsonElement>(d.Value);}
            }
            string request=JsonSerializer.Serialize(new{operation=Operation,inputs});
            string response=request==cachedRequest?cachedResponse:RunPython(request);
            using(var doc=JsonDocument.Parse(response)) {
                if(doc.RootElement.TryGetProperty("error",out var err))throw new Exception(err.GetString());
                int j=0;foreach(var val in doc.RootElement.GetProperty("outputs").EnumerateArray()) {
                    if(val.ValueKind==JsonValueKind.Object)da.SetData(j,new SolarData(val.GetRawText()));
                    else if(val.ValueKind==JsonValueKind.Array)da.SetDataList(j,val.EnumerateArray().Select(e=>e.ValueKind==JsonValueKind.String?(object)e.GetString():e.GetDouble()).ToArray());
                    else da.SetData(j,val.GetDouble());j++;
                }
            }
            cachedRequest=request;cachedResponse=response;
        }catch(Exception e){AddRuntimeMessage(GH_RuntimeMessageLevel.Error,e.Message);}
    }
    static string RunPython(string request) {
        string folder=Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        string root=Directory.GetParent(Directory.GetParent(folder).FullName).FullName;
        string python=Path.Combine(root,".venv","bin","python");
        if(!File.Exists(python))throw new FileNotFoundException("Python environment missing. Run scripts/build_plugin.sh in the repository.");
        var info=new ProcessStartInfo(python){UseShellExecute=false,RedirectStandardInput=true,RedirectStandardOutput=true,RedirectStandardError=true,CreateNoWindow=true};
        info.ArgumentList.Add(Path.Combine(folder,"bridge.py"));
        using(var process=Process.Start(info)) {
            var output=process.StandardOutput.ReadToEndAsync();var errors=process.StandardError.ReadToEndAsync();
            process.StandardInput.Write(request);process.StandardInput.Close();
            if(!process.WaitForExit(60000)){process.Kill(true);throw new TimeoutException("Solar calculation exceeded 60 seconds. Reduce the sample count.");}
            string text=output.GetAwaiter().GetResult();string error=errors.GetAwaiter().GetResult();
            if(string.IsNullOrWhiteSpace(text))throw new Exception("Python calculation failed: "+error);
            return text;
        }
    }
}
public class LocationComponent : SolarComponent { public LocationComponent():base("location"){} protected override string Operation=>"location"; public override Guid ComponentGuid=>new Guid("76dab4bb-c916-5b20-aa4b-32ec5e6da555"); }
public class ClearSkyComponent : SolarComponent { public ClearSkyComponent():base("clear_sky"){} protected override string Operation=>"clear_sky"; public override Guid ComponentGuid=>new Guid("1f252b9d-adb3-5595-86b3-9b6421f33bc8"); }
public class SunPositionComponent : SolarComponent { public SunPositionComponent():base("sun_position"){} protected override string Operation=>"sun_position"; public override Guid ComponentGuid=>new Guid("8a9973a5-dd98-5b24-9544-77bc86684b62"); }
public class PanelOrientationComponent : SolarComponent { public PanelOrientationComponent():base("panel_orientation"){} protected override string Operation=>"panel_orientation"; public override Guid ComponentGuid=>new Guid("84efa099-c974-5038-bf57-94f582ee4757"); }
public class IrradianceComponent : SolarComponent { public IrradianceComponent():base("irradiance"){} protected override string Operation=>"irradiance"; public override Guid ComponentGuid=>new Guid("dcd719ec-8aac-57fb-b434-83cf606aff95"); }
public class PvPowerComponent : SolarComponent { public PvPowerComponent():base("pv_power"){} protected override string Operation=>"pv_power"; public override Guid ComponentGuid=>new Guid("b37acf51-1872-579a-8713-a2f8a42614fa"); }
public class EnergyComponent : SolarComponent { public EnergyComponent():base("energy"){} protected override string Operation=>"energy"; public override Guid ComponentGuid=>new Guid("78819c5b-7d6b-5962-ba8d-efe4b48e24cf"); }
}
