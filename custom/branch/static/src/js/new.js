/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { symmetricalDifference } from "@web/core/utils/arrays";
import { session } from "@web/session";
var ajax = require('web.ajax');
var rpc = require('web.rpc');


function parseBranchIds(bidsFromHash) {
    const bids = [];
    if (typeof bidsFromHash === "string") {
        bids.push(...bidsFromHash.split(",").map(Number));
    } else if (typeof bidsFromHash === "number") {
        bids.push(bidsFromHash);
    }
    return bids;
}

//function computeAllowedBranchIds(bids) {
//    const { user_branches } = session;
//    let allowedBranchIds = bids || [];
//    const availableBranchesFromSession = user_branches.allowed_branches;
//    const notReallyAllowedBranches = allowedBranchIds.filter(
//        (id) => !(id in availableBranchesFromSession)
//    );
//
//    if (!allowedBranchIds.length || notReallyAllowedBranches.length) {
//        allowedBranchIds = [user_branches.current_branch];
//    }
//    return allowedBranchIds;
//}

export const branchService = {
    dependencies: ["user", "router", "cookie"],
    async start(env, { user, router, cookie }) {
        let bids;
        var list = [];
        var dict = {};
        var self = this;
        this.list = [];
        this.allowedBranchIds = [];
        this.company = 0;
        const { user_companies } = session;
        const availablecompany = env.services.company.allowedCompanyIds;
        const currentcompany = env.services.company.currentCompany;

        await rpc.query({
            model: 'res.users',
            method: 'get_branch_ids',
            args: [session.uid,availablecompany, currentcompany]
        }).then(function(data){
            self.list.push(data['allowed_branch_ids'])
            self.allowedBranchIds = data['branch_ids']
            self.company = data['company_id']
            self.currentCompanyId = data['currentCompanyId']
            self.currentbranch = data['current_branch']

        })
        const branches = self.list[0]
        const availableBranches = self.list[0]
        if ("bids" in router.current.hash) {
            bids = parseBranchIds(router.current.hash.bids);
        } else if ("bids" in cookie.current) {
            bids = parseBranchIds(cookie.current.bids);
        }
        let allowedBranchIds = [];
        const availableBranchesFromSession = self.allowedBranchIds;
        const notReallyAllowedBranches = allowedBranchIds.filter(
            (id) => !(id in availableBranchesFromSession)
        );
        const branch_data = self.allowedBranchIds;
        if (bids == undefined){
            bids = [self.allowedBranchIds[0]];
        }
        let same = (arr1, arr2) => bids.every(v => arr1.includes(v));
        if (!allowedBranchIds.length || notReallyAllowedBranches.length) {
            // console.log('___ xsxscs : ', self.allowedBranchIds,self.allowedBranchIds.reverse(), bids)
            if(same(branch_data, bids) == false){
                allowedBranchIds = [self.allowedBranchIds[0]];
            }
            else{
                allowedBranchIds = bids;
            }
        }

        return {
            availableBranches,
            branches,
            get allowedBranchIds() {
                return allowedBranchIds.slice();
            },
            get currentBranch() {
                ajax.jsonRpc('/set_brnach_rule', 'call', {
                            'allowledbid':  allowedBranchIds,
                            'BranchID':  allowedBranchIds[0],
                    })
                return availableBranches[allowedBranchIds[0]];
            },
            setBranches(mode, ...branchIds) {
                // compute next company ids
                let nextBranchIds;
                if (mode === "toggle") {
                    nextBranchIds = symmetricalDifference(allowedBranchIds, branchIds);
                } else if (mode === "loginto") {
                    const branchId = branchIds[0];
                    if (allowedBranchIds.length === 1) {
                        // 1 enabled company: stay in single company mode
                        nextBranchIds = [branchId];
                    } else {
                        // multi company mode
                        nextBranchIds = [
                            branchId,
                            ...allowedBranchIds.filter((id) => id !== branchId),
                        ];
                    }
                }
                let branchId = nextBranchIds;
                nextBranchIds = branchId.length ? branchId : [branchIds[0]];
                // apply them
                router.pushState({ bids: nextBranchIds }, { lock: true });
                cookie.setCookie("bids", nextBranchIds);

                ajax.jsonRpc('/set_brnach', 'call', {
                            'BranchID':  nextBranchIds,
                    })
                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
            },
        };
    },
};

registry.category("services").add("branch", branchService);
