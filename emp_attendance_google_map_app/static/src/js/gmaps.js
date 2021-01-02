    odoo.define('emp_attendance_google_map_app.gmaps', function (require) {
    "use strict";
        var AbstractAction = require('web.AbstractAction');
        var core = require('web.core');
        var ajax = require('web.ajax');
        var FormController = require('web.FormController');
        var FormRenderer = require('web.FormRenderer');
        var FormView = require('web.FormView');
        var QWeb = core.qweb;
        var _t = core._t;


        FormRenderer.include({

            _addOnClickMapAction: function ($el, node) {
                var self = this;
                $el.click(function () {
                    self.trigger_up('load_map', {
                        attrs: node.attrs,
                        record: self.state,
                    });
                });
            },
            _renderHeaderButton: function (node) {
                var $button = this._super.apply(this, arguments);
                this._addOnClickMapAction($button, node);
                return $button;
            },

            _renderStatButton: function (node) {
                var $button = this._super.apply(this, arguments);
                this._addOnClickMapAction($button, node);
                return $button;
            },


        });


        FormController.include({

            custom_events: _.extend({}, FormController.prototype.custom_events, {
                load_map: '_onLoadMap',
            }),

            events: _.extend({}, FormController.prototype.events, {
                'click .search_emp_login': '_onClickEmpLogin',
            }),

            className: 'my_map_button',

            init: function () {
                this._super.apply(this, arguments);
            },

            _onLoadMap: function (event) {
                var self = this;
                if(event.data.record){
                    if(event.data.record.model == 'odoo.map') {
                        if(event.data.record.data) {
                            if(event.data.record.data.id) {
                                var id = event.data.record.data.id;
                            }
                            else{
                                var id = '';
                            }
                            if(event.data.record.data.employee_id) {
                                var emp = event.data.record.data.employee_id.res_id;
                            }
                            else{
                                var emp = '';
                            }

                            if(event.data.record.data.map_key) {
                                var mapkey = event.data.record.data.map_key;
                            
                            }
                            else{
                                var mapkey = '';
                            }

                            if(event.data.record.data.date) {
                                var date = event.data.record.data.date;
                            }
                            else{
                                var date = '';
                            }

                            if(mapkey != ''){

                                var div = document.createElement('div');
                                div.setAttribute('class', 'myscript');
                                $("head").append(div);

                                var s = document.createElement("script");
                                s.type = "text/javascript";
                                s.src = mapkey;
                                $("div.myscript").append(s);

                                ajax.jsonRpc('/mylocation/address','call', {id : id, emp : emp, date : date}).then(function(data){
                                    var location_data = data;
                                    self.initialize_stores(location_data);
                                });
                            }
                            else{
                                alert(_t("No Data Found."));
                            }
                        }
                    }
                }
            },


            initialize_stores: function(data) {

                var final_data = JSON.parse(data)

                if(jQuery.isEmptyObject(final_data)) {

                    alert(_t("No Data Found."));

                }else{

                    var mapProp={
                        center : new google.maps.LatLng(final_data.map_init.latitude,final_data.map_init.longitude),zoom:final_data.map_init.map_zoom,mapTypeId:final_data.map_init.map_type
                    };
                    var latlng = {lat: parseFloat(final_data.map_init.latitude), lng: parseFloat(final_data.map_init.longitude)};        
                    var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
                    map.setZoom(16);
                    var infowindow = new google.maps.InfoWindow;
                    var addr = '<div class="gmap">';
                    if(final_data.map_init.image){
                        addr+='<div class="store-image"><img style="height:50px;width:50px;" src="'+final_data.map_init.image+'"/></div>';
                    }
                    if(final_data.map_init.employee){
                        addr+='<div class="store-name">'+final_data.map_init.employee+'</div>';
                    } 
                    addr += '<div class="search_emp_login" t-att-data-id="'+final_data.map_init.employee+'" t-att-data-date="'+final_data.map_init.date+'"><i class="fa fa-list fa-3x" t-att-data-id="'+final_data.map_init.employee+'" t-att-data-date="'+final_data.map_init.date+'"/></div></div>'
                    infowindow.setContent(addr);
                    var marker = new google.maps.Marker({
                        position: latlng,
                        map: map
                      });
                    infowindow.open(map, marker);
                }
            },

            _onClickEmpLogin: function (event) {
                
                var self = this;
                var $el = $(event.currentTarget);

                var emp_id = $(this).data('fa-list', $(this).attr('data-id'));

                var emp = emp_id[0].initialState.data.employee_id.res_id
                var date = emp_id[0].initialState.data.date._i

                ajax.jsonRpc('/myattendance','call', {emp : emp, date : date}).then(function(data){
                    if(jQuery.isEmptyObject(data)) {
                        alert(_t("Something Went Wrong. Refresh and Try again!!."));
                    }else{
                        data = JSON.parse(data);
                        var action = {
                            type: 'ir.actions.act_window',
                            res_model: 'hr.attendance',
                            views: [[false, 'list'], [false, 'form']],
                            view_type: "list",
                            view_mode: "list",
                            domain : [['id', '=', data]],
                            target: 'new'
                        };
                        self.do_action(action)
                    }
                });

            }

        });

    });
