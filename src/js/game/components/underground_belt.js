import { BaseItem } from "../base_item";
import { Component } from "../component";
import { globalConfig } from "../../core/config";
import { types } from "../../savegame/serialization";
import { gItemRegistry } from "../../core/global_registries";

/** @enum {string} */
export const enumUndergroundBeltMode = {
    sender: "sender",
    receiver: "receiver",
};

export class UndergroundBeltComponent extends Component {
    static getId() {
        return "UndergroundBelt";
    }

    static getSchema() {
        return {
            mode: types.enum(enumUndergroundBeltMode),
            pendingItems: types.array(types.pair(types.obj(gItemRegistry), types.float)),
            tier: types.uint,
        };
    }

    /**
     *
     * @param {object} param0
     * @param {enumUndergroundBeltMode=} param0.mode As which type of belt the entity acts
     * @param {number=} param0.tier
     */
    constructor({ mode = enumUndergroundBeltMode.sender, tier = 0 }) {
        super();

        this.mode = mode;
        this.tier = tier;

        /** @type {Array<{ item: BaseItem, progress: number }>} */
        this.consumptionAnimations = [];

        /**
         * Used on both receiver and sender.
         * Reciever: Used to store the next item to transfer, and to block input while doing this
         * Sender: Used to store which items are currently "travelling"
         * @type {Array<[BaseItem, number]>} Format is [Item, remaining seconds until transfer/ejection]
         */
        this.pendingItems = [];
    }

    /**
     * Tries to accept an item from an external source like a regular belt or building
     * @param {BaseItem} item
     * @param {number} beltSpeed How fast this item travels
     */
    tryAcceptExternalItem(item, beltSpeed) {
        if (this.mode !== enumUndergroundBeltMode.sender) {
            // Only senders accept external items
            return false;
        }

        if (this.pendingItems.length > 0) {
            // We currently have a pending item
            return false;
        }

        this.pendingItems.push([item, 0]);
        return true;
    }

    /**
     * Tries to accept a tunneled item
     * @param {BaseItem} item
     * @param {number} travelDistance How many tiles this item has to travel
     * @param {number} beltSpeed How fast this item travels
     */
    tryAcceptTunneledItem(item, travelDistance, beltSpeed) {
        if (this.mode !== enumUndergroundBeltMode.receiver) {
            // Only receivers can accept tunneled items
            return false;
        }

        // Notice: We assume that for all items the travel distance is the same
        const maxItemsInTunnel = (2 + travelDistance) / globalConfig.itemSpacingOnBelts;
        if (this.pendingItems.length >= maxItemsInTunnel) {
            // Simulate a real belt which gets full at some point
            return false;
        }

        // NOTICE:
        // This corresponds to the item ejector - it needs 0.5 additional tiles to eject the item.
        // So instead of adding 1 we add 0.5 only.
        // Additionally it takes 1 tile for the acceptor which we just add on top.
        const travelDuration = (travelDistance + 1.5) / beltSpeed / globalConfig.itemSpacingOnBelts;

        this.pendingItems.push([item, travelDuration]);

        // Sort so we can only look at the first ones
        this.pendingItems.sort((a, b) => a[1] - b[1]);

        return true;
    }
}
