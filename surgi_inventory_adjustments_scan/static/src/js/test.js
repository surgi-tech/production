//odoo.define('surgitech_inventory_adjustments_scan.adjScan', function (require) {
//    "use strict";
//
////    var core = require('web.core');
////    var ListView = require('web.ListView');
////    var ListController = require("web.ListController");
////
////    var IncludeListView = {
////
////        renderButtons: function() {
////            this._super.apply(this, arguments);
////            if (this.modelName === "stock.inventory.line") {
////                var summary_apply_leave_btn = this.$buttons.find('button.o_start_scan_adjust');
////                summary_apply_leave_btn.on('click', this.proxy('starts_scan'))
////            }
////        },
////        starts_scan: function(){
////        console.log("action start");
////            var self = this;
////            var action = {
////                         type: 'ir.actions.act_window',
////                        res_model: 'stock.inventory',
////                        res_id: parseInt(this.activeid),
////                        views: [[false, 'form']],
////                        target: 'main',
////            };
////            console.log("action fired");
////            return this.do_action(action);
////        },
////        activeid:function(){
////           var lochash = location.hash.substr(1);
////            var activeid = lochash.substr(lochash.indexOf('id='))
////                    .split('&')[0]
////                    .split('=')[1];
////            return activeid;
////        },
////
////    };
//
//
//
//var core = require("web.core");
//    var Widget = require("web.Widget");
//    var _t = core._t;
//    var QWeb = core.qweb;
//    var rpc = require('web.rpc');
//     var ListView = require('web.ListView');
//    var ListController = require("web.ListController");
//    var ScanningModel = Backbone.Model.extend({
//        initialize: function (session, attributes) {
//            Backbone.Model.prototype.initialize.call(this, attributes);
//            this.active_id = this.get_stock_id();
//            this.ready = this.load_stock_data();
//            this.data = {};
//            this.products = {};
//            this.codeProducts = {}
//            this.scan_lines = {}
//            this.addedScansObj = {};
//            this.totalQty = 0;
//            this.createdScansObj = {};
//        },
//        get_stock_id: function () {
//            var lochash = location.hash.substr(1);
//            var activeid = lochash.substr(lochash.indexOf('id='))
//                    .split('&')[0]
//                    .split('=')[1];
//            return activeid;
//        },
//        load_stock_data: function () {
//            var loaded = new $.Deferred();
//            var self = this;
//            var stock_inventory = rpc.query({
//                model:'stock.inventory',
//                method: 'get_stock_inventory_scan_data',
//                args: [self.active_id],
//            }).then(function (result) {
//                result = JSON.parse(result);
//                self.scan_lines = result.scan_lines;
//                self.data = result.data;
//                self.products = result.products;
//                self.codeProducts = result.productsCodeData;
//                self.res = result.res;
//                self.res_id = result.res_id;
//                self.addedScansObj = {};
//                self.totalQty = 0;
//                self.createdScansObj = {};
//                loaded.resolve();
//            });
//            return loaded;
//        }
//    });
//    var adjScanning = Widget.extend({
//        template: "adjScanning",
//        events: {
//            "click .cancel_button": "cancel_button",
//            "click .deleteScan": "deleteScan",
//            "change .qty": "calculateTotalQty",
//            "keyup .qty": "calculateTotalQty",
//            "change #scan_box": "search_product",
//            "click .selectLine": "selectLine",
//            "click .save_button": function () {
//                var self = this;
//                var stock_inventory = rpc.query({
//                    model:'stock.inventory',
//                    method: 'scan_from_ui',
//                    args: [self.stock_data.res_id, self.stock_data.createdScansObj, self.stock_data.addedScansObj],
//                }).then(function (server_ids) {
//                    self.do_action({
//                        type: 'ir.actions.act_window',
//                        res_model: 'stock.inventory',
//                        res_id: parseInt(self.stock_data.active_id),
//                        views: [[false, 'form']],
//                        target: 'main',
//                    });
//                });
//            }
//        },
//        init: function (parent) {
//            this._super(parent);
//            this.stock_data = new ScanningModel(require);
//        },
//        start: function () {
//            var sup = this._super();
//            var self = this;
//            return this.stock_data.ready.done(function () {
//                self.$el.prepend();
//                setTimeout(function () {
//                    $('input#scan_box').focus();
//
//                    var scan_lines_count = Object.keys(self.stock_data.scan_lines).length;
//                    if (scan_lines_count > 0) {
//                        for (var i = 0; i < scan_lines_count; i++) {
//                            var scan_box = self.stock_data.scan_lines[i]['serial'];
//                            if(scan_box){
//                                if (!self.stock_data.addedScansObj[scan_box]) {
//                                    self.stock_data.addedScansObj[scan_box] = {};
//                                }
//                                var encoded = CryptoJS.MD5(scan_box);
//                                var qty = parseInt(self.stock_data.scan_lines[i]['qty']);
//                                var product_id = self.stock_data.scan_lines[i]['product_id'];
//                                var product = self.stock_data.products[product_id]
//                                var countProducts = Object.keys(self.stock_data.data[scan_box]).length;
//                                for (var j = 0; j < countProducts; j++) {
//                                    var line = self.stock_data.data[scan_box][j];
//                                    var line_product = self.stock_data.products[line['product_id']];
//                                    if (line_product['id'] == product_id) {
//                                        var prod_lot_id = line['id'];
//                                        break;
//                                    }
//                                }
//                                self.stock_data.addedScansObj[scan_box][product_id] = {'product_id': product['id'], 'product_uom_id': product['uom_id'], 'location_id': self.stock_data.res.location_id, 'prod_lot_id': prod_lot_id, 'package_id': self.stock_data.res.package_id, 'partner_id': self.stock_data.res.partner_id, 'theoretical_qty': 0, 'product_qty': 0, 'state': self.stock_data.res.state, 'scanned_quantity': qty};
//                                console.log(self.stock_data.addedScansObj[scan_box][product_id]);
//                                var html = '<tr id="' + encoded + '"><td><input type="hidden" class="lineProductId" value="' + product['id'] + '" />' + product['name'] + '</td><td>' + self.stock_data.res.location_name + '</td><td><span class="scan_box_line">' + scan_box + '</span></td><td>' + self.stock_data.res.partner_id + '</td><td>0</td><td>0</td><td><input type="number" class="qty" value="' + qty + '"/></td><td style="cursor:pointer;" class="deleteScan"><span class="fa fa-trash-o" name="delete"></span></td></tr>';
//                                $('table tbody').append(html);
//                                self.stock_data.totalQty += qty;
//                            }
//                        }
//                        $('span.totalQty').html(self.stock_data.totalQty);
//                    }
//                    $('.loadingWait').hide();
//                }, 1000);
//            });
//        },
//        selectLine: function (e) {
//            var self = this;
//            var el = e.target;
//            var scan_box = $(el).attr('id');
//            var encoded = CryptoJS.MD5(scan_box);
//            var product_id = $(el).val();
//            var product = self.stock_data.products[product_id];
//            var found = false;
//            var input = false;
//            $("input.lineProductId").each(function () {
//                if ($(this).val() == product_id && $(this).parent('td').parent('tr').attr('id') == encoded) {
//                    found = true;
//                    input = $(this);
//                    return false;
//                }
//            });
//            if (found == true) {
//                var tRow = $(input).parent('td').parent('tr');
//                var qtyInput = tRow.find('input.qty');
//                var qty = parseInt(qtyInput.val()) + 1;
//                qtyInput.val(qty);
//            } else {
//                var scan = false;
//                var countProducts = Object.keys(self.stock_data.data[scan_box]).length;
//                for (var i = 0; i < countProducts; i++) {
//                    var line = self.stock_data.data[scan_box][i];
//                    var line_product = self.stock_data.products[line['product_id']];
//                    if (line_product['id'] == product_id) {
//                        scan = line;
//                        break;
//                    }
//                }
//                var qty = 1;
//                var html = '<tr id="' + encoded + '"><td><input type="hidden" class="lineProductId" value="' + product['id'] + '" />' + product['name'] + '</td><td>' + self.stock_data.res.location_name + '</td><td><span class="scan_box_line">' + scan_box + '</span></td><td>' + self.stock_data.res.partner_id + '</td><td>0</td><td>0</td><td><input type="number" class="qty" value="' + qty + '"/></td><td style="cursor:pointer;" class="deleteScan"><span class="fa fa-trash-o" name="delete"></span></td></tr>';
//                $('table tbody').append(html);
//            }
//            if (!self.stock_data.addedScansObj[scan_box]) {
//                self.stock_data.addedScansObj[scan_box] = {};
//            }
//            if (!self.stock_data.addedScansObj[scan_box][product_id]) {
//                self.stock_data.addedScansObj[scan_box][product_id] = {'prod_lot_id': scan['id'], 'product_id': product['id'], 'product_uom_id': self.stock_data.res.uom_id, 'location_id': self.stock_data.res.location_id, 'package_id': self.stock_data.res.package_id, 'partner_id': self.stock_data.res.partner_id, 'theoretical_qty': 0, 'product_qty': 0, 'state': self.stock_data.res.state, 'scanned_quantity': 1};
//            } else {
//                self.stock_data.addedScansObj[scan_box][product_id].scanned_quantity += 1;
//            }
//            $('#productCode').html(product['default_code']);
//            $('#productName').html(product['name']);
//            $('#productSerial').html(scan_box);
//            $('#productsList').html();
//            $('#productsList').hide();
//            $('input#scan_box').val('').blur().focus();
//            self.stock_data.totalQty += 1;
//            $('span.totalQty').html(self.stock_data.totalQty);
//        },
//        calculateTotalQty: function (e) {
//            var self = this;
//            var el = e.target;
//            var newQty = 0;
//            $('.qty').each(function (el) {
//                var value = $(this).val();
//                if (value == '')
//                    value = 0;
//                newQty += parseInt(value);
//            });
//            var tRow = $(el).parent('td').parent('tr');
//            var qty = tRow.find('input.qty').val();
//            if (qty == '')
//                qty = 0;
//            var scan_box = tRow.find('span.scan_box_line').html();
//            var product_id = tRow.find('input.lineProductId').val();
//            if (self.stock_data.createdScansObj[scan_box] && self.stock_data.createdScansObj[scan_box][product_id]) {
//                self.stock_data.createdScansObj[scan_box][product_id].scanned_quantity = qty;
//            }
//            self.stock_data.addedScansObj[scan_box][product_id].scanned_quantity = qty;
//            console.log(tRow, qty, self.stock_data.addedScansObj[scan_box][product_id]);
//            self.stock_data.totalQty = newQty;
//            $('span.totalQty').html(self.stock_data.totalQty);
//        },
//        deleteScan: function (e) {
//            var self = this;
//            var el = e.target;
//            if (el.nodeName != 'TD') {
//                el = $(el).parent();
//            }
//            var tRow = $(el).parent('tr');
//            var qty = tRow.find('input.qty').val();
//            var scan_box = tRow.find('span.scan_box_line').html();
//            var product_id = tRow.find('input.lineProductId').val();
//            if (self.stock_data.createdScansObj[scan_box] && self.stock_data.createdScansObj[scan_box][product_id]) {
//                delete self.stock_data.createdScansObj[scan_box][product_id];
//            }
//            delete self.stock_data.addedScansObj[scan_box][product_id];
//            self.stock_data.totalQty -= parseInt(qty);
//            $('span.totalQty').html(self.stock_data.totalQty);
//            tRow.remove();
//            $('#productCode').html('');
//            $('#productName').html('');
//            $('#productSerial').html('');
//            $('table').focus();
//            $('input#scan_box').focus();
//        },
//        search_product: function (e) {
//            var self = this;
//            var scan_box = $('#scan_box').val();
//            if (scan_box.trim() != '') {
//                var modalShown = false;
//                $("div[id$=Modal]").each(function () {
//                    if (($(this).data('bs.modal') || {}).isShown) {
//                        document.getElementById('audio').play();
//                        $('#scan_box').val('').blur().focus();
//                        modalShown = true;
//                    }
//                });
//                if ($('#productsList').css('display') !== 'none') {
//                    document.getElementById('audio').play();
//                    modalShown = true;
//                }
//                if (modalShown == false) {
//                    var encoded = CryptoJS.MD5(scan_box);
//                    if (self.stock_data.data[scan_box] != undefined) {
//                        var countProducts = Object.keys(self.stock_data.data[scan_box]).length;
//                        if (countProducts == 1) {
//                            var scan = self.stock_data.data[scan_box][0];
//                            console.log(scan['id']);
//                            var product_id = scan.product_id;
//                            var product = self.stock_data.products[product_id];
//                            var lot_name = scan.lot_name;
//                            var qty = 1;
//                            if (!self.stock_data.createdScansObj[scan_box]) {
//                                self.stock_data.createdScansObj[scan_box] = {};
//                            }
//                            if (!self.stock_data.addedScansObj[scan_box]) {
//                                self.stock_data.addedScansObj[scan_box] = {};
//                            }
//                            if (self.stock_data.addedScansObj[scan_box][product_id]) {
//                                var tr = $('#' + encoded);
//                                var qtyInput = tr.find('.qty');
//                                qty = parseInt(tr.find('.qty').val());
//                                qtyInput.val(qty + 1);
//                                if (self.stock_data.createdScansObj[scan_box][product_id]) {
//                                    self.stock_data.createdScansObj[scan_box][product_id].product_qty = qty + 1;
//                                }
//                                self.stock_data.addedScansObj[scan_box][product_id].scanned_quantity = qty + 1;
//                                $('#productCode').html(self.stock_data.products[product_id]['default_code']);
//                                $('#productName').html(self.stock_data.products[product_id]['name']);
//                                $('#productSerial').html(scan_box);
//                                self.stock_data.totalQty += 1;
//                                $('span.totalQty').html(self.stock_data.totalQty);
//                            } else {
//                                var product = self.stock_data.products[product_id];
//                                if (self.stock_data.res.scanning_mode === 'internal_ref' && product.tracking !== 'none') {
//                                    $("#trackingModal").dialog({modal: true, open: function () {
//                                            $(this).parent().focus();
//                                        }});
//                                    beep();
//                                } else {
//                                    self.stock_data.addedScansObj[scan_box][product_id] = {'product_id': product['id'], 'product_uom_id': self.stock_data.res.uom_id, 'location_id': self.stock_data.res.location_id, 'prod_lot_id': scan['id'], 'package_id': self.stock_data.res.package_id, 'partner_id': self.stock_data.res.partner_id, 'theoretical_qty': 0, 'product_qty': 0, 'state': self.stock_data.res.state, 'scanned_quantity': qty};
//                                    var html = '<tr id="' + encoded + '"><td><input type="hidden" class="lineProductId" value="' + product['id'] + '" />' + product['name'] + '</td><td>' + self.stock_data.res.location_name + '</td><td><span class="scan_box_line">' + scan_box + '</span></td><td>' + self.stock_data.res.partner_id + '</td><td>0</td><td>0</td><td><input type="number" class="qty" value="' + qty + '"/></td><td style="cursor:pointer;" class="deleteScan"><span class="fa fa-trash-o" name="delete"></span></td></tr>';
//                                    $('table.o_list_view tbody').append(html);
//                                    $('#productCode').html(product['default_code']);
//                                    $('#productName').html(product['name']);
//                                    $('#productSerial').html(scan_box);
//                                    self.stock_data.totalQty += 1;
//                                    $('span.totalQty').html(self.stock_data.totalQty);
//                                }
//                            }
//                        } else {
//                            document.getElementById('audio').play();
//                            var linesHtml = 'Please select a product from the list:<br /><br />';
//                            for (var i = 0; i < countProducts; i++) {
//                                var line = self.stock_data.data[scan_box][i];
//                                var product = self.stock_data.products[line['product_id']];
//                                linesHtml += '<input type="radio" value="' + product['id'] + '" class="selectLine" id="' + scan_box + '" /> [' + product['default_code'] + '] ' + product['name'] + '<br />';
//                            }
//                            $('#productsList').html(linesHtml);
//                            $('#productsList').show();//.focus();
//                        }
//                    } else {
//                        if (self.stock_data.res.scanning_mode === 'lot_serial_no') {
//                            if (scan_box.indexOf('$') !== -1) {
//                                lot_name = scan_box.split('$')[0];
//                            } else {
//                                lot_name = '-';
//                            }
//                            // date separated by / or -
//                            var serial = scan_box;
//                            var token = '/';
//                            if (scan_box.indexOf('/') === -1) {
//                                token = '-';
//                            }
//                            if (scan_box.split(token)[1] !== undefined) {
//                                var extracted_year = scan_box.split(token)[1].slice(0, 4);
//                                var extracted_month = scan_box.split('#')[1].slice(0, 2);
//                                var month = extracted_month.replace(/^['0']*/, "");
//                                var exp_dat = extracted_year + "-" + month + "-" + '01';
//                                var internal_ref = scan_box.split(token)[1].slice(4);
//                                // 2025-09-01 620006220
//                                console.log(exp_dat, internal_ref);
//                                if (!self.stock_data.codeProducts[internal_ref]) {
//                                    document.getElementById('audio').play();
//                                    $("#productNotFoundModal").modal();
//                                } else {
//                                    var product = self.stock_data.codeProducts[internal_ref];
//                                    var qty = 1;
//                                    var html = '<tr id="' + encoded + '"><td><input type="hidden" class="lineProductId" value="' + product['id'] + '" />' + product['name'] + '</td><td>' + self.stock_data.res.location_name + '</td><td><span class="scan_box_line">' + scan_box + '</span></td><td>' + self.stock_data.res.partner_id + '</td><td>0</td><td>0</td><td><input type="number" class="qty" value="' + qty + '"/></td><td style="cursor:pointer;" class="deleteScan"><span class="fa fa-trash-o" name="delete"></span></td></tr>';
//                                    $('table tbody').append(html);
//                                    if (!self.stock_data.addedScansObj[serial]) {
//                                        self.stock_data.addedScansObj[serial] = {};
//                                    }
//                                    if (!self.stock_data.createdScansObj[serial]) {
//                                        self.stock_data.createdScansObj[serial] = {};
//                                    }
//                                    self.stock_data.addedScansObj[serial][product['id']] = {'prod_lot_id_ref': serial, 'product_id': product['id'], 'product_uom_id': self.stock_data.res.uom_id, 'location_id': self.stock_data.res.location_id, 'package_id': self.stock_data.res.package_id, 'partner_id': self.stock_data.res.partner_id, 'theoretical_qty': 0, 'product_qty': 0, 'state': self.stock_data.res.state, 'scanned_quantity': 1};
//                                    self.stock_data.createdScansObj[serial][product['id']] = {'product_id': product['id'], 'product_qty': 1, 'name': serial, 'lot_name': lot_name, 'expiration_date': exp_dat};
//                                    self.stock_data.data[serial] = [{'product_id': product['id'], 'lot_name': lot_name}];
//                                    self.stock_data.totalQty += 1;
//                                    $('span.totalQty').html(self.stock_data.totalQty);
//                                    $('table').show();
//                                    $('#productCode').html(self.stock_data.codeProducts[internal_ref]['default_code']);
//                                    $('#productName').html(self.stock_data.codeProducts[internal_ref]['name']);
//                                    $('#productSerial').html(scan_box);
//                                }
//                            } else {
//                                document.getElementById('audio').play();
//                                $("#invalidLotModal").modal();
//                            }
//                        } else {
//                            document.getElementById('audio').play();
//                            $("#warningModal").modal();
//                        }
//                    }
//                }
//                $('#scan_box').val('').blur().focus();
//            }
//        },
//        cancel_button: function (e) {
//            var self = this;
//            self.do_action({
//                type: 'ir.actions.act_window',
//                res_model: 'stock.inventory',
//                res_id: parseInt(self.stock_data.active_id),
//                views: [[false, 'form']],
//                target: 'main',
//            });
//        }
//    });
//
//    var IncludeListView = {
//
//        renderButtons: function() {
//            this._super.apply(this, arguments);
//            if (this.modelName === "stock.inventory.line") {
//                var summary_apply_leave_btn = this.$buttons.find('button.o_start_scan_adjust');
//                summary_apply_leave_btn.on('click', this.proxy('starts_scan'))
//            }
//        },
//        starts_scan: function(){
//        console.log("action start");
//            var self = this;
//            var action = {
//                         type: 'ir.actions.act_window',
//                        res_model: 'stock.inventory',
//                        res_id: parseInt(this.activeid),
//                        views: [[false, 'form']],
//                        target: 'main',
//            };
//            console.log("action fired");
//            return this.do_action(action);
//        },
//        activeid:function(){
//           var lochash = location.hash.substr(1);
//            var activeid = lochash.substr(lochash.indexOf('id='))
//                    .split('&')[0]
//                    .split('=')[1];
//            return activeid;
//        },
//
//    };
//    ListController.include(IncludeListView);
//});