# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logging = logging.getLogger(__name__)

class IrModelForbid(models.Model):
    _name = 'ir.model.forbid'
    _description = 'Model forbid'

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True, help='If you uncheck the active field, it will disable the ACL without deleting it (if you delete a native ACL, it will be re-created when you reload the module).')
    model_id = fields.Many2one('ir.model', string='Object', required=True, domain=[('transient', '=', False)], index=True, ondelete='cascade')
    group_id = fields.Many2one('res.groups', string='Group', ondelete='cascade', index=True)
    perm_read = fields.Boolean(string='Read forbid')
    perm_write = fields.Boolean(string='Write forbid')
    perm_create = fields.Boolean(string='Create forbid')
    perm_unlink = fields.Boolean(string='Delete forbid')


class IrModel(models.Model):
    _inherit = 'ir.model'

    forbid_ids = fields.One2many('ir.model.forbid', 'model_id', string='禁止')



class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        r = super(IrModelAccess, self).check(model,mode,raise_exception)
        # _logging.info('checkcheckcheckcheckcheck-----------')
        # We check if a specific rule exists
        self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                              FROM ir_model_forbid a
                              JOIN ir_model m ON (m.id = a.model_id)
                              JOIN res_groups_users_rel gu ON (gu.gid = a.group_id)
                             WHERE m.model = %s
                               AND gu.uid = %s
                               AND a.active IS TRUE""".format(mode=mode),
                         (model, self._uid,))
        einfo = self._cr.fetchone()[0]
        if  einfo and raise_exception:
            msg_heads = {
                # Messages are declared in extenso so they are properly exported in translation terms
                'read': _("Sorry, you are not allowed to access this document."),
                'write':  _("Sorry, you are not allowed to modify this document."),
                'create': _("Sorry, you are not allowed to create this kind of document."),
                'unlink': _("Sorry, you are not allowed to delete this document."),
            }
            msg_tail = _("Please contact your system administrator if you think this is an error.") + "\n\n(" + _("Document model") + ": %s)"
            msg_params = (model,)
            msg_tail += ' - ({} {}, {} {})'.format(_('Operation:'), mode, _('User:'), self._uid)
            _logging.info('Access Denied by ACLs for operation: %s, uid: %s, model: %s', mode, self._uid, model)
            msg = '%s %s' % (msg_heads[mode], msg_tail)
            raise AccessError(msg % msg_params)

        return r