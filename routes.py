import pages.school
import time


# this is called app for swithing between pages 
# redirects based on the pages 
# @lru_cache(maxsize=10)
def get_layout(pathname):
    t0 = time.time()
    print(f"get_layout CALLED for: {pathname}")
    if pathname == "/karachi":
        from pages.karachi import get_karachi_layout
        
        layout = get_karachi_layout()
        return layout
    elif pathname == "/sukkur":
        from pages.sukkur import layout as sukkur_layout
        return sukkur_layout
    elif pathname == "/hyderabad":
        from pages.hyderabad import layout as hyderabad_layout
        return hyderabad_layout
    elif pathname == "/banbhore":
        from pages.banbhore import layout as banbhore_layout
        return banbhore_layout
    elif pathname == "/mirpurkhas":
        from pages.mirpurkhas import layout as mirpurkhas_layout
        return mirpurkhas_layout
    elif pathname == "/larkana":
        from pages.larkana import layout as larkana_layout
        return larkana_layout
    elif pathname == "/sehwan":
        from pages.sehwan import layout as sehwan_layout
        return sehwan_layout
    elif pathname == "/school":
        from pages.school import layout as school_layout
        print(pathname)
        return school_layout
    elif pathname in ["/", "/home"]:
        from pages.home import layout as home_layout
        return home_layout
    else:
        return None
