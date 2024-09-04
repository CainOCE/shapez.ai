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


class Mod extends shapez.Mod {
    init() {
        console.log("Shapez.ai Module Initialized");


        // Sandbox Mode
        this.modInterface.replaceMethod(shapez.Blueprint, "getCost", function () {
            return 0;
        });
        this.modInterface.replaceMethod(shapez.HubGoals, "isRewardUnlocked", function () {
            return true;
        });


        /* Calls a custom event when keybind is pressed. */
        function custom_event() {
            this.dialogs.showInfo("Mod Message", "It worked!");
            // this.root.hud.signals.notification.dispatch(
            //     "It worked!",
            //     shapez.enumNotificationType.info
            // );
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
                //TODO: Fix the custom event to fire.
                //custom_event();
                this.dialogs.showInfo("Mod Message", "It worked!");
                return shapez.STOP_PROPAGATION;
            },
        });


        /**
         * Places a building of type at x, y
         *
         * @param {type} buildingType - Shapez.Meta{*}Building Type
         * @param {type} x - Horizontal Map Position, Left to Right
         * @param {type} y - Vertical Map Position, Top to Bottom
         * @returns {type} None
         */
        function place_building(buildingType, x, y) {

            console.dir(buildingType)

            // Define a building to be placed
            const building = shapez.gMetaBuildingRegistry.findByClass(buildingType).createEntity({
                root: shapez,
                origin: new shapez.Vector(x, y),
                rotation: 0,
                originalRotation: 0,
                rotationVariant: 0,
                variant: "default",
            });

            // Add new building to appropriate lists.
            shapez.BaseMap.placeStaticEntity(building);
            shapez.EntityManager.registerEntity(building);
        }

        // console.dir(root)
        console.dir(shapez)
        // Ryan: Place belt and extractor
        // place_building(shapez.MetaBeltBuilding, 3, 4);
        place_building(shapez.MetaMinerBuilding, 3, 5);


        /**
         * Transforms the current gameState to a form readable by our model.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        function transform_data(gameState) {
            if (gameState == null) { return; }  // Guard Clause

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
             * to work per chunck, we can get entities perchuck in the map
             * gamestate if need
             */

            // Process State
            if (gameState["key"] == "InGameState") {
                var newGameState = [];

                // 1. Extract Entities
                var entity_list = [];
                var entities = gameState["core"]["root"]["entityMgr"]["entities"];
                for (let i = 0; i < entities.length; i++) {
                    let new_entity = this.extractRelevantDataEntity(entities[i]);
                    entity_list.push(new_entity);
                }
                //newGameState.push(entity_list);

                // 2. Extract Goals
                var goal = gameState["core"]["root"]["hubGoals"]["currentGoal"];
                let transfferedGoal = this.extractRelevantDataGoal(goal);
                newGameState.push(transfferedGoal);

                // 3. Extract Map
                var mapChunkList = [];
                var map = gameState["core"]["root"]["map"]["chunksById"];
                for (const [key, value] of map) {
                    let dict = {};
                    dict[key] = this.extractRelevantDataMap(value);
                    mapChunkList.push(dict);
                }
                //newGameState.push(mapChunckList);

                // Send test package to Python Backend
                var test = await sendGameStateToPython(newGameState);
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
