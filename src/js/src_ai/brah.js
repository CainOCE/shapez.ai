import { Mod } from "../mods/mod";
import { StateManager } from "../core/state_manager";
export class Sender {
    constructor(current) {
        // var state = new StateManager(app);
        // var current = state.getCurrentState();
        this.transform_data(current);
    }

    transform_data(gameState) {
        if (gameState == null) {
            return;
        }
        if (gameState["key"] == "InGameState") {
            var entities = gameState["core"]["root"]["entityMgr"]["entities"];

            // console.log(gameState);
            var goal = gameState["core"]["root"]["hubGoals"];
            var map = gameState["core"]["root"]["map"]["chunksById"];
            console.log(map);
        }
    }

    SendToAPI() {}
}
