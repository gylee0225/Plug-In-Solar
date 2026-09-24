"""JSON-only bridge; no arbitrary code execution or pickle deserialization."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
import pandas as pd
from plug_in_solar import core

def decode(v):
    if isinstance(v,dict) and v.get('kind')=='frame':
        idx=pd.to_datetime(v['index'],utc=True).tz_convert(v['timezone'])
        return pd.DataFrame(v['data'],index=idx)
    if isinstance(v,dict) and v.get('kind')=='site':
        return core.location(**v['data'])
    return v

def encode(v):
    if isinstance(v,pd.DataFrame):
        return dict(kind='frame',index=[t.isoformat() for t in v.index],timezone=str(v.index.tz),data={c:v[c].tolist() for c in v.columns})
    return v

def dispatch(op,a):
    a={k:decode(v) for k,v in a.items()}
    if op=='location':
        core.location(**a)
        return [dict(kind='site',data=a)]
    if op=='clear_sky':
        w=core.clear_sky(**a); return [w,[t.isoformat() for t in w.index]]
    if op=='sun_position':
        s=core.sun_position(a['site'],a['weather'].index)
        return [s,s.apparent_elevation.tolist(),s.azimuth.tolist()]
    if op=='panel_orientation': return list(core.orientation(*a['normal'],a['north_deg']))
    if op=='irradiance':
        p=core.irradiance(**a); return [p,p.poa_global.tolist()]
    if op=='pv_power':
        a['poa']=a['poa'].poa_global
        p=core.pv_power(**a); return [p,p.dc_w.tolist(),p.ac_w.tolist()]
    if op=='energy': return [core.energy_kwh(a['power'].ac_w,a['step_hours'])]
    raise ValueError('Unknown component: '+op)

if __name__=='__main__':
    try:
        req=json.load(sys.stdin)
        print(json.dumps({'outputs':[encode(v) for v in dispatch(req['operation'],req['inputs'])]},allow_nan=False))
    except Exception as e:
        print(json.dumps({'error':str(e)})); sys.exit(1)
