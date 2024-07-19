

# %%
from engine_v1.datamodel import PDL
pdl = PDL()
# pdl.parse_PDL_str()
pdl.load_from_file("/work/huabu/data/v240628/huabu_refine01/000-114挂号.txt")
pdl

# %%
pdl.parse_PDL_str()
# %%
def parse_pdl(pdl_str):
    spliter = "\n\n"
    split_parts = pdl_str.split(spliter, 4)    # TODO: parse according to the header of each part
    parts = {}
    for p in split_parts:
        if p.startswith("APIs"):
            parts["apis"] = pdl._parse_apis(p)
        elif p.startswith("REQUESTs"):
            parts["requests"] = pdl._parse_apis(p)
        elif p.startswith("ANSWERs"):
            parts["answers"] = pdl._parse_apis(p)
        elif p.startswith("==="):
            parts["taskflow"], parts["taskflow_desc"] = pdl._parse_meta(p)
        else:
            if "workflow" in parts:
                print(f"[WARNING] {parts['workflow']} v.s. {p}")
            parts["workflow"] = p
    return parts

parts = parse_pdl(pdl.PDL_str)
parts
# %%
