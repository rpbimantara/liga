odoo.define('persebaya.PersebayaJadwal', function (require) {
"use strict";

var form_widget = require('web.form_widgets');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;

form_widget.WidgetButton.include({
    on_click: function() {
         if(this.node.attrs.string === "Squad Away"){

            // YOUR CODE
            alert("ASDASDASDASDASD+++++++++ASDASDASDASDAS+_+@)$+@*!(_$(_!@$&!@(&*$()@!&)$!@()&$()!@&$()");

            return;
         }
         this._super();
    },
});
});