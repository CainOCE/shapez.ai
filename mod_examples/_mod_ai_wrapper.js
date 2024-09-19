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
// need the list of goals
// need a way to send the static required amount i dont know if we can because the way we have it at the moment we have it we only send through it once
// List of shit
// CuCuCuCu
// ----CuCu
// RuRuRuRu
// RuRU----
// Cu----Cu
// Cu------
// CrCrCrCr
// RbRb----
// CpCpCpCp
// ScScScSc
// CgScScCg
// CbCbCbRb:CwCwCwCw
// RpRpRpRp:CwCwCwCw
// --Cg----:--Cr----
// SrSrSrSr:CyCyCyCy
// SrSrSrSr:CyCyCyCy:SwSwSwSw
// CbRbRbCb:CwCwCwCw:WbWbWbWb
// Sg----Sg:CgCgCgCg:--CyCy--
// CpRpCp--:SwSwSwSw
// RuCw--Cw:----Ru--
// CrCwCrCw:CwCrCwCr:CrCwCrCw:CwCrCwCr
// Cg----Cr:Cw----Cw:Sy------:Cy----Cy
// CcSyCcSy:SyCcSyCc:CcSyCcSy
// CcRcCcRc:RwCwRwCw:Sr--Sw--:CyCyCyCy
// Rg--Rg--:CwRwCwRw:--Rg--Rg
// CbCuCbCu:Sr------:--CrSrCr:CwCwCwCw

class Mod extends shapez.Mod {
    init() {
        console.log("Shapez.ai Module Initialized");
        //console.log("root:", this.root);

        // Sandbox Mode
        this.modInterface.replaceMethod(shapez.Blueprint, "getCost", function () {
            return 0;
        });
        this.modInterface.replaceMethod(shapez.HubGoals, "isRewardUnlocked", function () {
            return true;
        });

        // save current or quit current game then make a new one wont work as we need the mod laughcher ot stay running ?? or not or do we just need app.py running, can do this way??
        function newGame(root) {
            // quits games
            root.gameState.goBackToMenu();
        }

        /**
         * Simplifies the inbuilt tryPlaceBuilding Method
         *
         * @param {MetaBuilding} building class of MetaBuilding to place
         * @param {number} X offset
         * @param {number} y offsetparam0.rotation
         * @returns {Entity}
         */
        function tryPlaceSimpleBuilding(root, building, x, y) {
            // console.log("root: ", root);
            return root.logic.tryPlaceBuilding({
                origin: new shapez.Vector(x, y),
                building: shapez.gMetaBuildingRegistry.findByClass(building),
                originalRotation: 0,
                rotation: 0,
                variant: "default",
                rotationVariant: 0,
            });
        }

        /* Simplifies the notification system. */
        function simpleNotification(root, msg) {
            // Display a message when called
            root.hud.signals.notification.dispatch(msg, shapez.enumNotificationType.info);
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
                // var u = tryPlaceSimpleBuilding(root, shapez.MetaMinerBuilding, -16, -10);
                // var v = tryPlaceSimpleBuilding(root, shapez.MetaMinerBuilding, 3, 5)

                transform_data(root);
                //newGame(root);

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
            if (gameState == null) {
                return;
            } // Guard Clause
            simpleNotification(root, "Gathering gameState...");

            // TODO:  Can this process/strategy be simplified?
            function extractRelevantColumnsEntity(entities) {
                let entitiesList = [];
                for (let i = 0; i < entities.length; i++) {
                    var direction = null;
                    let entityList = [];
                    let entity = entities[i]["components"];

                    // get position of entity
                    let xTile = entity["StaticMapEntity"]["origin"]["x"];
                    let yTile = entity["StaticMapEntity"]["origin"]["y"];

                    // 0 is north, 90 is east, 180 is south, 270 is west
                    let rotation = entity["StaticMapEntity"]["rotation"];

                    // gets the type of the enitity
                    let type;
                    if (entity["ItemProcessor"] != null) {
                        type = entity["ItemProcessor"]["type"];
                    } else if (entity["UndergroundBelt"] != null) {
                        type = entity["UndergroundBelt"]["mode"];
                    } else if (entity["Miner"] != null) {
                        type = "Miner";
                    } else if (entity["Belt"]) {
                        type = "Belt";
                        direction = entity["Belt"]["direction"];
                    } else {
                        throw new Error("no registered Entity");
                    }

                    //pushs components to an array
                    entityList.push(type);
                    entityList.push(xTile);
                    entityList.push(yTile);
                    entityList.push(rotation);
                    entityList.push(direction);
                    entitiesList.push(entityList);
                }
                return entitiesList;
            }

            function staticGoal(stored, goal, required) {
                // need a way to not count the ones already in once a level is complete
                for (let key in stored) {
                    if (key == goal) {
                        required -= stored[key];
                    }
                }
                return required;
            }

            // calculates each resource position and puts it in a dictionary
            function calculateResourcePosition(map, dict) {
                // Goes through lower layer array and gets a resource
                for (let i = 0; i < 16; ++i) {
                    for (let j = 0; j < 16; ++j) {
                        // select a tile within the chunk
                        var resource = map["lowerLayer"][i][j];

                        // stores type and position of resource
                        if (resource instanceof shapez.ColorItem) {
                            let temp = [];
                            let filtered_colour = resource["color"];
                            temp.push(filtered_colour);
                            temp.push(i + map["tileX"]);
                            temp.push(j + map["tileY"] - 1);
                            dict.push(temp);
                        } else if (resource instanceof shapez.ShapeItem) {
                            let temp = [];
                            let filtered_shape = resource["definition"]["cachedHash"];
                            temp.push(filtered_shape);
                            temp.push(i + map["tileX"]);
                            temp.push(j + map["tileY"]);
                            dict.push(temp);
                        }
                    }
                }
                return dict;
            }

            // TODO: Chunks or map?
            /**
             * depends how we want to do it but it might be easier
             * to work per chunk, we can get entities per chunk in the map
             * gamestate if need
             */

            // Process State
            if (gameState["key"] == "InGameState") {
                // Contains three arrays 1. Entities 2. hub goal 3. resources
                var filteredGameState = [];

                // 1. Extract Entities [Type, X (Tile), Y (Tile), Rotation, direction]
                simpleNotification(root, "Extracting Entities...");
                var entity_list = [];
                var entities = gameState["core"]["root"]["entityMgr"]["entities"];

                entity_list = extractRelevantColumnsEntity(entities);
                filteredGameState.push(entity_list);

                // 2. Extract Goals [Goal ID of shape, static amount]
                simpleNotification(root, "Extracting Goals...");
                var stored = gameState["core"]["root"]["hubGoals"]["storedShapes"];
                var level = gameState["core"]["root"]["hubGoals"]["level"];
                var goal = gameState["core"]["root"]["hubGoals"]["currentGoal"];
                let transfferedGoal = [];
                var statics = staticGoal(stored, goal["definition"]["cachedHash"], goal["required"]);
                
                transfferedGoal.push(goal["definition"]["cachedHash"]);
                transfferedGoal.push(statics);
                // transfferedGoal.push(goal["required"]);
                filteredGameState.push(transfferedGoal);

                // 3. Extract Map [type, X (Tile), Y (Tile)]
                simpleNotification(root, "Extracting Map Features...");
                var mapChunkList = [];
                var map = gameState["core"]["root"]["map"]["chunksById"];
                let dict = [];
                for (const [key, value] of map) {
                    dict = calculateResourcePosition(value, dict);
                }
                mapChunkList.push(dict);

                filteredGameState.push(mapChunkList);

                console.log(filteredGameState);
                // Send test package to Python Backend
                simpleNotification(root, "Querying AI Model...");
                var test = sendGameStateToPythongameState(filteredGameState);
                console.log(test);
                simpleNotification(root, "AI Model Query Complete");
            }
        }

        /**
         * Receives a signal from the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        function receive_signal() {
            return;
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
