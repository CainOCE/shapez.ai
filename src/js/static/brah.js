import { Mod } from "../mods/mod";
import { StateManager } from "../core/state_manager";
export class Sender {
    constructor(current) {
        // var state = new StateManager(app);
        // var current = state.getCurrentState();
        this.transform_data(current);
    }

    extractRelevantDataEnitiy(entity) {
        return {
            components: entity.components,
            uid: entity.uid,
        };
    }

    extractRelevantDataGoal(goal) {
        return {
            definiton: goal.definition,
            required: goal.required,
        };
    }

    extractRelevantDataMap(map) {
        return {
            contents: map.contents,
            lowerLayer: map.lowerLayer,
            patches: map.patches,
            tileSpaceRectangle: map.tileSpaceRectangle,
            tileX: map.tileX,
            tileY: map.tileY,
            worldSpaceRectangle: map.worldSpaceRectangle,
            x: map.x,
            y: map.y,
        };
    }

    async transform_data(gameState) {
        if (gameState == null) {
            return;
        }
        if (gameState["key"] == "InGameState") {
            var newGameState = [];
            var entity_list = [];
            // depends how we want to do it but it might be easier to work per chunck, we can get entities perchuck in the map gamestate if need
            var entities = gameState["core"]["root"]["entityMgr"]["entities"];
            for (let i = 0; i < entities.length; i++) {
                let new_enitiy = this.extractRelevantDataEnitiy(entities[i]);
                entity_list.push(new_enitiy);
            }
            //newGameState.push(entity_list);
            var goal = gameState["core"]["root"]["hubGoals"]["currentGoal"];
            let transfferedGoal = this.extractRelevantDataGoal(goal);
            newGameState.push(transfferedGoal);
            var map = gameState["core"]["root"]["map"]["chunksById"];
            //console.log(map);
            var mapChunckList = [];
            for (const [key, value] of map) {
                let dict = {};
                dict[key] = this.extractRelevantDataMap(value);
                mapChunckList.push(dict);
            }
            //console.log(newGameState);
            //newGameState.push(mapChunckList);
            var test = await sendGameStateToPython(newGameState);
            console.log(test);
        }
    }
}

async function sendGameStateToPython(gameState) {
    try {
        const response = await fetch("http://127.0.0.1:5000/process", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ game_state: gameState }),
        });
        const data = await response.json();
        return data.move;
    } catch (error) {
        console.error("Error:", error);
    }
}
