/**
Class which will action changes to the game in place of player
**/
import { MetaBeltBuilding } from "./buildings/belt";
import { MetaBlockBuilding } from "./buildings/block";
import { gMetaBuildingRegistry } from "../core/global_registries";
import { defaultBuildingVariant } from "./meta_building";
import { globalConfig } from "../core/config";
import { Vector } from "../core/vector";
import { MetaBuilding } from "./meta_building";
import { MetaMinerBuilding } from "./buildings/miner";

export class ShapezBot {
    constructor(root) {
        this.root = root; // The game instance, which you need to interact with
        this.init();
    }

    init() {
        console.log("Bot initialized");
        // Add initialization logic here
        // Place the belt
        const belt = gMetaBuildingRegistry.findByClass(MetaBeltBuilding).createEntity({
            root: this.root,
            origin: new Vector(3, 4),
            rotation: 0,
            originalRotation: 0,
            rotationVariant: 0,
            variant: defaultBuildingVariant,
        });
        const extract = gMetaBuildingRegistry.findByClass(MetaMinerBuilding).createEntity({
            root: this.root,
            origin: new Vector(3, 5),
            rotation: 0,
            originalRotation: 0,
            rotationVariant: 0,
            variant: defaultBuildingVariant,
        });
        this.root.map.placeStaticEntity(belt);
        this.root.entityMgr.registerEntity(belt);
        this.root.map.placeStaticEntity(extract);
        this.root.entityMgr.registerEntity(extract);
        this.root.camera.center = new Vector(-5, 2).multiplyScalar(globalConfig.tileSize);
    }
}
