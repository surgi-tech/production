odoo.define('website_hr_recruitment.tour', function(require) {
    'use strict';

    var tour = require("web_tour.tour");

    tour.register('website_hr_recruitment_tour', {
        test: true,
        url: '/jobs/apply/3',
    }, [{
        content: "Complete name",
        trigger: "input[name=partner_name]",
        run: "text John Smith"
    }, {
        content: "Complete Email",
        trigger: "input[name=email_from]",
        run: "text john@smith.com"
    },

    {
        content: "Complete Address",
        trigger: "input[name=address]",
        run: "text john@smith.com"
    },

    {
        content: "Complete Qualification",
        trigger: "input[name=qualification]",
        run: "text john@smith.com"
    },

    {
        content: "Complete Training Courses",
        trigger: "input[name=training_courses]",
        run: "text john@smith.com"
    },

    {
        content: "Complete Previous Experience",
        trigger: "input[name=previous_experience]",
        run: "text john@smith.com"
    },

    {
        content: "Complete Age",
        trigger: "input[name=age]",
        run: "text john@smith.com"
    },
    {
            content: "Complete Nominee",
            trigger: "input[name=nominee]",
            run: "text john@smith.com"
        },

    {
            content: "Complete Gender",
            trigger: "input[name=gender]",
            run: "text john@smith.com"
            },




    {
        content: "Complete phone number",
        trigger: "input[name=partner_phone]",
        run: "text 118.218"
    }, {
        content: "Complete Subject",
        trigger: "textarea[name=description]",
        run: "text ### HR RECRUITMENT TEST DATA ###"
    }, { // TODO: Upload a file ?
        content: "Send the form",
        trigger: ".o_website_form_send"
    }, {
        content: "Check the form is submited without errors",
        trigger: ".oe_structure:has(h1:contains('Congratulations'))"
    }]);

    return {};
});
