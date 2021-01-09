jQuery(document).ready(function () {
    window.newWindow = null
});
function openAdjustmentScanWindow(loadedStockLotScanData) {
    if (window.newWindow != null) {
        window.newWindow.close();
        window.newWindow = null;
    }
    window.newWindow = window.open("", "mywindow", 'screenX=1,screenY=1,left=1,top=1,scrollbars=1,menubar=0,location=0,resizable=1,width=' + screen.availWidth + ',height=' + screen.availHeight);
    var interval = setInterval(checkAdjustmentNewWindow, 1000);
    function checkAdjustmentNewWindow() {
        if (window.newWindow != null) {
            clearInterval(interval);
            var closeInterval = setInterval(checkAdjustmentNewWindowClosed, 1000);
            function checkAdjustmentNewWindowClosed() {
                if ((window.newWindow == null) || (window.newWindow.closed)) {
                    clearInterval(closeInterval);
                    window.location.reload();
                }
            }
            var result = JSON.parse(loadedStockLotScanData);
            var url = result.scanUrl;
            jQuery(window.newWindow.document.body).html('<form method="post" action="' + url + '"><input type="hidden" name="result" id="result" /></form>');
            var inputResult = jQuery(window.newWindow.document.body).find("input#result");
            inputResult.val(loadedStockLotScanData);
            var form = jQuery(window.newWindow.document.body).find("form");
            form.submit();
        }
    }


}

function getScanWindowAdjustmentData() {
    var hashtag = window.location.hash.substr(1);
    var vars = hashtag.split("&");
    var id = 0;
    for (var i = 0; i < vars.length; i++) {
        var params = vars[i].split("=");
        if (params[0] == 'id') {
            id = params[1];
        }
    }
    jQuery('a:contains("Start Scan")').hide();
    odoo.define('surgitech_inventory_adjustments_scan.stock_inventory_scan_data', function (require) {
        "use restrict";
        var Model = require('web.Model');
        var stock_pecking_model = new Model('stock.inventory');
        stock_pecking_model.call('get_stock_inventory_scan_data', [id]).then(function (loadedStockLotScanData) {
            openAdjustmentScanWindow(loadedStockLotScanData);
        });
    });
}

function checkScanningMode() {
    var scanningMode = jQuery('select[name="scanning_mode"]').val();
    if (scanningMode == 'false') {
        alert('You should select scanning mode first !!');
    } else if (scanningMode == undefined) {
        if (jQuery("label:contains('Scanning Mode')").parent().next().children('span').html().toString() == '') {
            alert('You should select scanning mode first !!');
        } else {
            getScanWindowAdjustmentData();
        }
    } else {
        getScanWindowAdjustmentData();
    }
}
