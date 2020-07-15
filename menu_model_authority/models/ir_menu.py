# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
_logging = logging.getLogger(__name__)
class inher_user(models.Model):
    _inherit = "res.users"
    menu_ids = fields.Many2many('ir.ui.menu',string=u"菜单")

class inher_menus(models.Model):
    _inherit = 'ir.ui.menu'
    hide_for_user = fields.Many2many('res.users',string="用户")
    hide_group_ids = fields.Many2many('res.groups',string="组")

    action_type = fields.Char(compute='_compute_action_type')
    model_id = fields.Many2one('ir.model',string='模型',compute='_compute_model_id')

    @api.model
    def _compute_action_type(self):
        for menu in self:
            if(menu.action):
                menu.action_type = menu.action.type

    @api.model
    def _compute_model_id(self):
        for menu in self:
            if(menu.action):
                if menu.action.type == 'ir.actions.act_window':
                    model_name = menu.action.res_model
                    # _logging.info(model_name)
                    model = self.env['ir.model'].search([('model','=',model_name)])
                    # _logging.info(model)
                    menu.model_id = model.id

    @api.model
    @api.returns('self')
    def get_user_roots(self):
        """ Return all root menu ids visible for the user.

        :return: the root menu ids
        :rtype: list(int)
        """
        menu_roots = super(inher_menus, self).get_user_roots()
        main_list = []
        lat_list = []
        for i in menu_roots:
            main_list.append(i.id)
            
        users = self.env.user
        if users.menu_ids:
            for menus in users.menu_ids:
                lat_list.append(menus.id)
            b = set(main_list) - set(lat_list)
                
            menu_roots = self.browse(b)
        return menu_roots

    @api.model
    @api.returns('self')
    def get_user_group(self):
        group_list ={}
        menus = self.search([])
        fields = ['hide_group_ids',]
        menus_data = menus.read(fields)
        # _logging.info(menus_data)
        for menu in menus_data:
            if(len(menu['hide_group_ids']) > 0):
                group_list[str(menu['id'])] = menu['hide_group_ids']
        # _logging.info(group_list)
        return group_list

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        menu_root = super(inher_menus, self).load_menus(debug)
        users = self.env.user
        hide_list = []
        if users.menu_ids:
            for menu in users.menu_ids:
                hide_list.append(menu.id)
        root_children = menu_root['children']

        group_list = self.get_user_group()
        user_groups = []
        for group in self.env.user.groups_id:
            user_groups.append(group.id)
        # _logging.info(user_groups)

        def lookallmenu(startNode):
            for node in startNode:
                iid = node['id']
                key = str(iid)
                children_root = node['children']
                if iid in hide_list:
                    # _logging.info(iid)
                    # 用户屏蔽
                    startNode.remove(node)
                elif key in group_list:
                    # 组屏蔽
                    groups = group_list[key]
                    for group in groups:
                        if group in user_groups and node in startNode:
                            startNode.remove(node)
                else:
                    lookallmenu(children_root)
        lookallmenu(root_children)
        
        return menu_root
  