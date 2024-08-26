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
        this.root = root;
        this.init();
    }

    init() {
        console.log("Bot initialized");
        // Place the belt
        this.place_building(MetaBeltBuilding, 3, 4);
        // place extractor
        this.place_building(MetaMinerBuilding, 3, 5);
    }

    /*places a building function of the specified type at the position (x,y)*/
    place_building(buildingType, x, y) {
        const building = gMetaBuildingRegistry.findByClass(buildingType).createEntity({
            root: this.root,
            origin: new Vector(x, y),
            rotation: 0,
            originalRotation: 0,
            rotationVariant: 0,
            variant: defaultBuildingVariant,
        });
        this.root.map.placeStaticEntity(building);
        this.root.entityMgr.registerEntity(building);
    }
}
