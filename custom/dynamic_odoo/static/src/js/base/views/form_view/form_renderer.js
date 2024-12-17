odoo.define('dynamic_odoo.FormRenderer', function (require) {

    var core = require('web.core');
    var FormRenderer = require('web.FormRenderer');
    var base = require('dynamic_odoo.base');
    var QWeb = core.qweb;
    var {ViewButton} = require("@web/views/view_button/view_button");
    var legacyEnv = require('web.commonEnv');
    var {registerPatch} = require('@mail/model/model_core');
    const Dialog = require('web.Dialog');
    const env = require('web.env');
    const {Component, onMounted, tags} = owl;


    registerPatch({
        name: 'MessagingNotificationHandler',
        recordMethods: {
            async _handleNotification(message) {
                if ((message || {}).type == "approval_data") {
                    this.env.services.bus_service.trigger('update_approval', message.payload.approval);
                    return true;
                }
                return this._super(message);
            },
        }
    });


    var ApprovalWidget = base.WidgetBase.extend({
        template: "Studio.Approval",
        init: function (parent, params) {
            this._super(parent, params);
            const {approval} = this.props;
            this.setApproval(approval);
        },
        _onUpdateApproval: function (approval) {
            this.setApproval(approval);
            if (this.ref.$details) {
                this.renderDetails();
            }
        },
        setApproval: function (approval) {
            const {user_groups} = legacyEnv;
            if (user_groups) {
                approval.map((ap) => {
                    if (!user_groups.includes(ap.group_id)) {
                        ap.disable = true;
                    }
                });
            }
            this.approval = approval;
        },
        onShowApproval: function (e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            this.renderDetails();
        },
        onClose: function () {
            this.ref.$details.remove();
        },
        onAction: function (e, stateUpdate) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            const recordId = $(e.currentTarget).parents(".apItem").attr("data") || "0", env = legacyEnv;
            env.services.rpc({
                model: "studio.approval.details",
                method: 'approval_update',
                args: [[parseInt(recordId)], {
                    state: stateUpdate,
                    user_accepted: env.session.uid,
                    date_accepted: this.dateToServer(new moment())
                }],
                kwargs: {},
            });
        },
        renderDetails: function () {
            if (!this.approval.length) {
                return;
            }
            if (this.ref.$details) {
                this.ref.$details.remove();
            }
            const {left, top} = this.$el.offset();
            this.ref.$details = $(QWeb.render("Studio.Approval.details", {approval: this.approval, widget: this}));
            $('body').append(this.ref.$details);
            this.ref.$details.css({
                top: 7 + top + this.$el.outerHeight() + "px",
                left: (left + 16 - this.ref.$details.outerWidth() / 5) + "px"
            });
            this.bindAction();
        },
        bindAction: function () {
            this.$el.find(".iAP").click(this.onShowApproval.bind(this));
            if (this.ref.$details) {
                this.ref.$details.find(".apItem:not([disable]) .aAccept").click((e) => this.onAction(e, "accept"));
                this.ref.$details.find(".apItem:not([disable]) .aDecline").click((e) => this.onAction(e, "decline"));
                this.ref.$details.find(".apItem:not([disable]) .aReset").click((e) => this.onAction(e, "wait"));
                $(window).click(this.onClose.bind(this));
                this.ref.$details.click((e) => e.stopPropagation());
            }
        }
    });


    const {patch} = require('web.utils');
    patch(ViewButton.prototype, 'studio.ViewButton', {
        setup() {
            this._super();
            const self = this;
            onMounted(() => {
                self.env.services.bus_service.addEventListener('update_approval', this._onUpdateApproval.bind(this));
                self._renderApproval();
            });
        },
        get clickParams() {
            const res = this._super();
            if (this.studioConfirm) {
                res.confirm = false;
            }
            return res;
        },
        getApprovalData() {
            const {button_id} = this.props.attrs || {};
            return button_id ? this.props.record.model.__bm__.localData[this.props.record.__bm_handle__].approval[button_id] || [] : false;
        },
        onClick(ev) {
            if (this.props.tag === "a") {
                ev.preventDefault();
            }
            const self = this,
                superFnc = this._super.bind(this), {button_id} = this.props.attrs || {}, {confirm} = this.props.clickParams,
                approvalData = this.getApprovalData();
            if (button_id) {
                if (approvalData && approvalData.filter((ap) => ["wait", "decline"].includes(ap.state)).length) {
                    return false
                }
                if (confirm) {
                    Dialog.studioConfirm(this, confirm, {
                        confirm_callback: async () => {
                            self.studioConfirm = true;
                            superFnc(ev);
                            self.studioConfirm = false;
                        },
                        cancel_callback: async () => {
                        },
                        html: true,
                        size: "medium"
                    });
                    return false
                }
            }
            this._super(ev);
        },
        _onUpdateApproval: function (approval) {
            const {button_id} = this.props.attrs || {};
            if (button_id) {
                this.props.record.model.__bm__.localData[this.props.record.__bm_handle__].approval = approval.detail;
                this.__owl__.refs.approval._onUpdateApproval(approval.detail[button_id]);
            }
        },
        _renderApproval: function () {
            const {button_approval, button_id} = this.props.attrs || {};
            if (button_approval) {
                const approvalData = (this.props.record.model.__bm__.localData[this.props.record.__bm_handle__].approval || {})[button_id] || [];
                const approval = new ApprovalWidget(this, {approval: approvalData});
                approval.appendTo(this.__owl__.bdom.child.el);
                this.__owl__.refs.approval = approval;
            }
        },
    });

    FormRenderer.include({
        init: function () {
            this._super.apply(this, arguments);
            odoo['studio'].env.services.bus_service.addEventListener('update_approval', this._onUpdateApproval.bind(this));
            this.ref = {approval: {}};
        },
        _onUpdateApproval: function (approval) {
            this.state.approval = approval;
            Object.keys(this.ref.approval).map((buttonId) => {
                if (buttonId in approval) {
                    this.ref.approval[buttonId]._onUpdateApproval(approval[buttonId]);
                }
            });
        },
        _renderApproval: function (node, $button) {
            if (node.attrs.button_approval) {
                const approvalId = node.attrs.button_id, approvalData = (this.state.approval || {})[approvalId] || [];
                const approval = new ApprovalWidget(this, {approval: approvalData, $button: $button});
                approval.appendTo($button);
                this.ref.approval[approvalId] = approval;
            }
        },
        _renderHeaderButton: function (node) {
            const $button = this._super(node);
            this._renderApproval(node, $button);
            return $button;
        },
        _renderTagButton: function (node) {
            const $button = this._super(node);
            this._renderApproval(node, $button);
            return $button;
        },
    });
});
