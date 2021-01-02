odoo.define('emp_attendance_google_map_app.my_attendances_extend', function (require) {
"use strict";

	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var ajax = require('web.ajax');
	var MyAttendances = require('hr_attendance.my_attendances');
	var GreetingMessage = require('hr_attendance.greeting_message')
	var QWeb = core.qweb;
	var _t = core._t;


	GreetingMessage.include({
		init: function(parent, action) {
			var self = this;
			this.address;
			this.os;
			this.browser;
			this._super.apply(this, arguments);
		},

		start: function () {
			var self = this;
			if (this.attendance.check_in){ 
				this.address;
				this.os;
				this.browser;
				var map = this.initMap();
				self.$('.o_hr_attendance_button_dismiss').hide();
				
			}
			return $.when(map, this._super())
		},
		welcome_message: function() {
			var self = this;
			var now = this.attendance.check_in.clone();
			this.return_to_main_menu = setTimeout( function() { self.do_action(self.next_action, {clear_breadcrumbs: true}); }, 25000);

			if (now.hours() < 5) {
				this.$('.o_hr_attendance_message_message').append(_t("Good night"));
			} else if (now.hours() < 12) {
				if (now.hours() < 8 && Math.random() < 0.3) {
					if (Math.random() < 0.75) {
						this.$('.o_hr_attendance_message_message').append(_t("The early bird catches the worm"));
					} else {
						this.$('.o_hr_attendance_message_message').append(_t("First come, first served"));
					}
				} else {
					this.$('.o_hr_attendance_message_message').append(_t("Good morning"));
				}
			} else if (now.hours() < 17){
				this.$('.o_hr_attendance_message_message').append(_t("Good afternoon"));
			} else if (now.hours() < 23){
				this.$('.o_hr_attendance_message_message').append(_t("Good evening"));
			} else {
				this.$('.o_hr_attendance_message_message').append(_t("Good night"));
			}
			if(this.previous_attendance_change_date){
				var last_check_out_date = this.previous_attendance_change_date.clone();
				if(now - last_check_out_date > 24*7*60*60*1000){
					this.$('.o_hr_attendance_random_message').html(_t("Glad to have you back, it's been a while!"));
				} else {
					if(Math.random() < 0.02){
						this.$('.o_hr_attendance_random_message').html(_t("If a job is worth doing, it is worth doing well!"));
					}
				}
			}
		},


		initMap: function() {
			if ("geolocation" in navigator){
				var OSName="Unknown OS";
				if (navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
				if (navigator.appVersion.indexOf("Mac")!=-1) OSName="MacOS";
				if (navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
				if (navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";
				self.os = OSName;
				var check_out;
				if(this.attendance) {
					if(!this.attendance.check_out){
						check_out = false;
					}
					else{
						check_out = true;
					}
				}
				self.browser = Object.keys(jQuery.browser)[0];
				this.$('.myos').text(self.os);
				this.$('.mybrowser').text(self.browser);
				var employee = this.attendance.employee_id[0];
				var attendance = this.attendance.id;
				navigator.geolocation.getCurrentPosition(function(position){
					self.lat = position.coords.latitude;
					self.long = position.coords.longitude;
					$.ajax({
						url: "/google/address",
						method: "GET",
						dataType: 'json',
						data: {lat : self.lat, long : self.long, emp : employee, browser : self.browser, os : self.os , attend : attendance},
						success: function(data) {
							if(data){

								self.address = data[0];
								$('.mylocation').text(self.address);
								$('.o_hr_attendance_button_dismiss').show();
							}   
							else{
								$('.o_hr_attendance_button_dismiss').show();
							}
						}
					});
				});
			// }
			}
		}
	});
});