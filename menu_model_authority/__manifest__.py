{
    "name": "hsp 菜单模型屏蔽",
    "summary": "菜单模型屏蔽",
    "version": "12.0.2.0.0",
    "category": "",
    "license": "LGPL-3",
    "author": "hsp",
    "website": "https://www.einfo-tech.com",
    "depends": [
        "base",
    ],
    "data": [
        "views/hide_menu.xml",
        "views/forbid_model.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [
        #"static/src/xml/*.xml",
    ],
    "external_dependencies": {
        #"python": ['py3o.template',],
        #"bin": [],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}