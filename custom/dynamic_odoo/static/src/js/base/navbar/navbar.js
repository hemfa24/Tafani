/** @odoo-module **/
const {NavBar} = require("@web/webclient/navbar/navbar");
const {patch} = require('web.utils');
const MenuEditor = require("view_center.menu_center");
const rootWidget = require("root.widget");
const {useService} = require("@web/core/utils/hooks");

const {Component} = owl;

class NavBarEdit extends Component {
    setup() {
        this.menuService = useService("menu")
    }
    onShowEdit() {
        const menuEditor = new MenuEditor(rootWidget, {menuService: this.menuService});
        menuEditor.appendTo($("body"));
    }
}

NavBarEdit.template = "studio.IconEdit";


patch(NavBar.prototype, 'view_center.navBar', {
    get currentAppSections() {
        return this._super();
    }
});

NavBar.components = {...NavBar.components, NavBarEdit};
