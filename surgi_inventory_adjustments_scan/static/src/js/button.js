//odoo.define('my_custom_module.my_custom_button', function (require) {
//"use strict";
//
//var core = require('web.core');
//var ajax = require('web.ajax');
//var ListView = require('web.ListView');
//var Dialog = require('web.Dialog');
//var web_client = require('web.web_client');
//
//var _t = core._t;
//var _lt = core._lt;
//var QWeb = core.qweb;
//console.log("1");
//ListView.include({
////console.log("2");
//    render_buttons: function($node) {
//        this._super($node)
//        var self = this;
//        console.log("3");
//        if (this.$buttons && this.model == 'stock.inventory.line') {
//            this.$GetIdsbutton = $(QWeb.render("my_custom_button", {'widget': this}));
//            this.$GetIdsbutton.appendTo(this.$buttons);
//            $(this.$buttons).find('.o_tree_custom_button').on('click', function() {
//                // Following route / method will be called when button is clicked
//                ajax.jsonRpc('/web/my_custom_method', 'call', {}).done(function() {
//                    self.reload_content()
//                })
//            });
//        }
//    },
//})
//});