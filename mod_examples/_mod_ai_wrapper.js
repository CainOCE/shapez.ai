// @ts-nocheck
const METADATA = {
    website: "https://tobspr.io",
    author: "fish-obsessed",
    name: "ShapeZ.ai",
    version: "0.0.1",
    id: "shapezai",
    description: "Facilitates communication via REST API with a python backend.",
    minimumGameVersion: ">=1.5.0",
};

// async function hotkey(root) {
//     const response = await makeCall(...);
//     placeBuildings(root, response);
// }

class Mod extends shapez.Mod {
    init() {
        console.log("Shapez.ai Module Initialized");
        console.log("root:", this.root);

        // Sandbox Mode
        this.modInterface.replaceMethod(shapez.Blueprint, "getCost", function () {
            return 0;
        });
        this.modInterface.replaceMethod(shapez.HubGoals, "isRewardUnlocked", function () {
            return true;
        });


        /**
         * Simplifies the inbuilt tryPlaceBuilding Method
         *
         * @param {MetaBuilding} building class of MetaBuilding to place
         * @param {number} X offset
         * @param {number} y offsetparam0.rotation
         * @returns {Entity}
         */
        function tryPlaceSimpleBuilding(root, building, x, y) {
            console.log("root: ", root)
            return root.logic.tryPlaceBuilding({
                origin: new shapez.Vector(x, y),
                building: shapez.gMetaBuildingRegistry.findByClass(
                    building
                ),
                originalRotation: 0,
                rotation: 0,
                variant: "default",
                rotationVariant: 0,
            });
        }


        /* Simplifies the notification system. */
        function simpleNotification(root, msg) {
            // Display a message when called
            root.hud.signals.notification.dispatch(
                msg,
                shapez.enumNotificationType.info
            );
        }


        // Register Custom keybinding
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_trigger",
            keyCode: shapez.keyToKeyCode("F"),
            translation: "trigger_custom_event",
            modifiers: {
                shift: true,
            },
            handler: root => {
                // TEST Ryan: Place belt and extractor
                // simpleNotification(root, "Ryan's Placement Test")
                // var u = tryPlaceSimpleBuilding(root, shapez.MetaBeltBuilding, 3, 4)
                // var v = tryPlaceSimpleBuilding(root, shapez.MetaMinerBuilding, 3, 5)

                transform_data(root)
                return shapez.STOP_PROPAGATION;
            },
        });


        /**
         * Transforms the current gameState to a form readable by our model.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        function transform_data(root) {
            var gameState = root.gameState;
            if (gameState == null) { return; }  // Guard Clause
            simpleNotification(root, "Gathering gameState...")

            // TODO:  Can this process/strategy be simplified?
            function extractRelevantDataEntity(entity) {
                return {
                    components: entity.components,
                    uid: entity.uid,
                };
            }

            function extractRelevantDataGoal(goal) {
                return {
                    definiton: goal.definition,
                    required: goal.required,
                };
            }

            function extractRelevantDataMap(map) {
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

            // TODO: Chunks or map?
            /**
             * depends how we want to do it but it might be easier
             * to work per chunk, we can get entities per chunk in the map
             * gamestate if need
             */

            // Process State
            if (gameState["key"] == "InGameState") {
                var newGameState = [];

                // 1. Extract Entities
                simpleNotification(root, "Extracting Entities...")
                var entity_list = [];
                var entities = gameState["core"]["root"]["entityMgr"]["entities"];
                for (let i = 0; i < entities.length; i++) {
                    let new_entity = extractRelevantDataEntity(entities[i]);
                    entity_list.push(new_entity);
                }
                newGameState.push(entity_list);

                // 2. Extract Goals
                simpleNotification(root, "Extracting Goals...")
                var goal = gameState["core"]["root"]["hubGoals"]["currentGoal"];
                let transfferedGoal = extractRelevantDataGoal(goal);
                newGameState.push(transfferedGoal);

                // 3. Extract Map
                simpleNotification(root, "Extracting Map Features...")
                var mapChunkList = [];
                var map = gameState["core"]["root"]["map"]["chunksById"];
                for (const [key, value] of map) {
                    let dict = {};
                    dict[key] = extractRelevantDataMap(value);
                    mapChunkList.push(dict);
                }
                newGameState.push(mapChunkList);

                // Send test package to Python Backend
                simpleNotification(root, "Querying AI Model...")
                var test = sendGameStateToPythongameState(newGameState);
                simpleNotification(root, "AI Model Query Complete")
                console.log(test);
            }
        }


        /**
         * Receives a signal from the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        function receive_signal() {
            return
        }

        /**
         * Sends a gameState obj to the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        async function sendGameStateToPythongameState(gameState) {
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
    }
}
