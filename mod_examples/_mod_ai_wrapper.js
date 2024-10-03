// @ts-nocheck
/*
Created on Tue Aug 13, 2024 at 09:55:35
@authors: Cain Bruhn-Tanzer, Shannon Searle, Ryan Miles
*/

const METADATA = {
    website: "https://tobspr.io",
    author: "fish-obsessed",
    name: "ShapeZ.ai",
    version: "0.0.1",
    id: "shapezai",
    description: "Communicates via REST API with a python backend.",
    minimumGameVersion: ">=1.5.0",
};

const resources = {
    // Colours
    "red": "r",
    "green": "g",
    "blue": "b",
    // NOTE:  Compound Colors do not exist on the map

    // Base Shapes
    "RuRuRuRu": "R",    // Rectangle
    "CuCuCuCu": "C",    // Circle
    "SuSuSuSu": "S",    // Star

    // Exists only Fractionally on the map eg XxWuXxXx etc
    "WuWuWuWu": "W",    // Windmill
}

class Mod extends shapez.Mod {

    init() {
        console.log("Shapez.ai Module Initialized");

        /* Sandbox Mode */
        this.modInterface.replaceMethod(shapez.Blueprint, "getCost", () => 0);
        this.modInterface.replaceMethod(
            shapez.HubGoals, "isRewardUnlocked", () => true
        );

        /* Executes code under development */
        function test(root) {
            // Place some various resources as a test.
            let x = 4
            place_resources(root, [
                {"type": "red", "x": x, "y":-3},
                {"type": "CuCuCuCu", "x": x, "y":-2},
                {"type": "RuRuRuRu", "x": x, "y":-1},
                {"type": "SuSuSuSu", "x": x, "y":0},
                {"type": "WuWuWuWu", "x": x, "y":1},

                {"type": "CuCuCuCu", "x": x+1, "y":-2},
                {"type": "RuRuRuRu", "x": x+1, "y":-1},
                {"type": "SuSuSuSu", "x": x+1, "y":0},

                {"type": "CuCuCuCu", "x": x+2, "y":-2},
                {"type": "RuRuRuRu", "x": x+2, "y":-1},

                {"type": "CuCuCuCu", "x": x+3, "y":-2},
            ])
        }

        /* Register "Reset Game" keybinding */
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_reset_trigger",
            keyCode: shapez.keyToKeyCode("R"),
            translation: "trigger_reset_event",
            modifiers: { shift: true, },
            handler: root => {
                // 'Hard' Reset the game, new seed and instance
                root.gameState.goBackToMenu();

                // 'Soft' reset the game. retain seed (and resouce locations)
                // softGameReset(root)

                return shapez.STOP_PROPAGATION;
            },
        });

        /* Register "AI Training" keybinding */
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_training_trigger",
            keyCode: shapez.keyToKeyCode("T"),
            translation: "trigger_training_event",
            modifiers: { shift: true, },
            handler: root => {
                train(root, getGameState(root))
                return shapez.STOP_PROPAGATION;
            },
        });

        /* Register "Trigger Function" keybinding */
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_query_trigger",
            keyCode: shapez.keyToKeyCode("Q"),
            translation: "trigger_query_event",
            modifiers: { shift: true, },
            handler: root => {
                query(root, getGameState(root));
                return shapez.STOP_PROPAGATION;
            },
        });

        /* Register "Trigger Function" keybinding */
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_test_function_trigger",
            keyCode: shapez.keyToKeyCode("F"),
            translation: "trigger_test_function_event",
            modifiers: { shift: true, },
            handler: root => {
                test(root)
                return shapez.STOP_PROPAGATION;
            },
        });

        /* Destroys all non-hub map entities and clears progression. */
        function softGameReset(root) {
            const E = root.gameState["core"]["root"]["entityMgr"]["entities"]
            // GUARD:
            if (E.size <= 1) {
                return
            }

            // Remove all Entities
            E.slice(1).forEach(e => {
                root.map.removeStaticEntity(e);
                root.entityMgr.destroyEntity(e);
            });
        }

        /* Places a ghost entity at the desired location */
        function addGhost(entities = []) { }

        /* Removes a single ghost entity. */
        function removeGhost(entities = []) { }

        /* Clears all ghost entities on the screen. */
        function clearGhosts(/* Clears all locally stored.*/) { }

        /* Plays a simple animated avatar, ShAIpEZy */
        function playAvatar() {
            /** TODO: What can Shapie do?
             *      - Play some nice animations or dialogue boxes.
             *      - Play a cool sound or audio track?
             *      (Dig in to the API and see if you can make somehting cool.)
             */
        }

        /**
         * Simplifies the inbuilt tryPlaceBuilding Method
         *
         * @param {MetaBuilding} building class of MetaBuilding to place
         * @param {number} X offset
         * @param {number} y offset
         * @param {number} rotation a number in [0, 90, 180, 270]
         * @returns {Entity}
         */
        function tryPlaceSimpleBuilding(root, building, x, y, rotation=0) {
            return root.logic.tryPlaceBuilding({
                origin: new shapez.Vector(x, y),
                building: shapez.gMetaBuildingRegistry.findByClass(
                    building
                ),
                originalRotation: 0,
                rotation: rotation,
                rotationVariant: 0,
                variant: "default",
            });
        }

        /* Places buildings given by the backend as a list solution. */
        function place_entities(root, entities) {
            console.dir(shapez.gMetaBuildingRegistry)
            for (let e of entities){
                const building = shapez.gMetaBuildingRegistry.findByClass(
                    shapez[`Meta${e.type}Building`],
                )
                root.logic.tryPlaceBuilding({
                    origin: new shapez.Vector(e.x, e.y),
                    building: building,
                    originalRotation: e.rotation,
                    rotation: e.rotation,
                    rotationVariant: 0,
                    variant: "default",
                });
            }
        }

        /**
         * Places a resource at a given location in the game.
         *
         * @param {Resource} resource class of resource to place
         * @param {number} X offset
         * @param {number} y offset
         * @returns {Item}
         */
        function tryPlaceResource(root, resource, x, y) {
            const COLORS = shapez.COLOR_ITEM_SINGLETONS
            const SHAPES = root.shapeDefinitionMgr

            // Get Chunk by x, y
            let map = root.gameState["core"]["root"]["map"]["chunksById"];
            let chunkId = `${Math.floor(x/16)}|${Math.floor(y/16)}`
            let chunk = map.get(chunkId)
            let item = null

            // GUARD:  Chunk not found
            if (!chunk) {
                console.warn(`Chunk not found for key: ${chunkId}`);
                return null;
            }

            // Resource is a colour
            if (Object.keys(COLORS).includes(resource)) {
                item = COLORS[resource]
            }

            // Resource is a shape
            if (shapez.ShapeDefinition.isValidShortKey(resource)) {
                item = root.shapeDefinitionMgr.getShapeItemFromDefinition(
                    shapez.ShapeDefinition.fromShortKey(resource)
                )
            }

            // Place Resource
            chunk.lowerLayer[(x%16+16)%16][(y%16+16)%16] = item;
            return item;
        }

        /* Places resources at the given locations */
        function place_resources(root, resources) {
            for (let r of resources){
                tryPlaceResource(
                    root,
                    r.type,
                    r.x, r.y,
                )
            }
        }

        /* Simplifies the notification system. */
        function simpleNotification(root, msg) {
            // Display a message when called
            root.hud.signals.notification.dispatch(
                msg,
                shapez.enumNotificationType.info
            );
        }


        /**
         * Transforms the current gameState to a form readable by our model.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        function getGameState(root) {
            var gameState = root.gameState;
            if (gameState == null || gameState["key"] !== "InGameState") {
                return;
            }

            // 1.  Extract Game Seed
            let seed = gameState["core"]["root"]["map"]["seed"];

            // 2.  Extract Level & Goal
            let level = gameState["core"]["root"]["hubGoals"]["level"];
            const G = gameState["core"]["root"]["hubGoals"]["currentGoal"];
            let goal = ({
                level: level,
                definition: G.definition,
                required: G.required,
            });

            // 3.  Extract Map (By Chunks for optimal resource scanning)
            const M = gameState["core"]["root"]["map"]["chunksById"];
            let chunks = Object.fromEntries(
                // Assume all chunks are 16x16 and hardcode
                Array.from(M.entries()).map(([key, chunk]) => [key, {
                    x: chunk.x,
                    y: chunk.y,
                    resources: chunk.lowerLayer,
                    patches: chunk.patches,
                }])
            );

            // 4.  Extract Entities
            const E = gameState["core"]["root"]["entityMgr"]["entities"]
            let entities = E.reduce((out, e) => {
                let ec = e.components;

                // Define Entity by Attached Components
                const getType = (ec) => {
                    // Define Entity by Attached Components
                    if (ec.Miner) return "miner";
                    if (ec.Belt) return "belt";
                    if (ec.UndergroundBelt) {
                        // type = ec.UndergroundBelt.mode;
                        // tier = ec.UndergroundBelt.tier;
                        // return `${type}${tier}`;
                    }
                    if (ec.ItemProcessor) return ec.ItemProcessor.type;
                    if (ec.Storage) return "storage";

                    // TODO Balancers are 'fun'
                    // console.log(ec)
                    return "Unknown";
                };

                /* Clean the entity description for the backend here. */
                const entity = {
                    type: getType(ec),
                    x: ec.StaticMapEntity.origin.x,
                    y: ec.StaticMapEntity.origin.y,
                    rotation: ec.StaticMapEntity.rotation,
                    direction: !!ec.Belt ? ec.Belt.direction : null,
                    mode: !!ec.UndergroundBelt ? ec.UndergroundBelt.mode : null,
                };

                out[e.uid] = entity;
                return out;
            }, {});

            // Fin. Return packaged gameState.
            return {
                seed: seed,
                map: chunks,
                level: level,
                goal: goal,
                entities: entities
            };
        }

        /* Sends a communication pulse to the Python Backend */
        async function ping() {
            var request = await fetch("http://127.0.0.1:5000/ping", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: "ping",
            })
                .then((response) => response.json())
                .then((data) => {
                    // Change indicator to show server comms are live
                    if (indicator.style.background == "lightgreen") {
                        update_indicator("green");
                    } else {
                        update_indicator("lightgreen");
                    }

                    // Call a reset if requested.
                })
                .catch((error) => {
                    update_indicator("red");
            });
            // NOTE:  It's super annoying that this generates an error
            //        constantly when it can't connect.  -net in the chrome
            //        devtools filter will hide these messages.
        }
        const intervalId = setInterval(async () => { await ping(); }, 1000);

        /**
         * Sends a gameState obj to the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        async function query(root, gameState) {
            update_indicator("yellow");
            var request = await fetch("http://127.0.0.1:5000/query", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(gameState),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Return Data:");
                    console.dir(data)
                    place_entities(root, data)
                    update_indicator("lightgreen");
                })
                .catch((error) => {
                    console.error("Request failed:", error);
                    update_indicator("red");
                });
        }

        /**
         * Sends a gameState obj to the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        async function train(root, gameState) {
            update_indicator("yellow");
            var request = await fetch("http://127.0.0.1:5000/train", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(gameState),
            })
                .then((response) => response.json())
                .then((data) => {
                    update_indicator("lightgreen");
                })
                .catch((error) => {
                    console.error("Request failed:", error);
                    update_indicator("red");
                });
        }

        /* Add AI Status indicator to bottom right of the Game UI */
        let indicator;
        this.modInterface.registerCss(`
            #shapez_ai_indicator {
                position: absolute; background: red;
                bottom: calc(10px * var(--ui-scale));
                right: calc(10px * var(--ui-scale));
                width: 12px; height: 12px; z-index: 1000;
                border: 2px solid white; border-radius: 50%; padding: 00px;
                display: flex; align-items: center; justify-content: center;
            }
        `);
        this.signals.stateEntered.add(state => {
            if (state instanceof shapez.InGameState) {
                // Create a div to house our element
                indicator = document.createElement("div");
                indicator.id = "shapez_ai_indicator";
                document.body.appendChild(indicator);

                // Cleanup when leaving the Game State
                this.signals.stateExited.add(exitState => {
                    if (exitState instanceof shapez.InGameState) {
                        document.body.removeChild(indicator);
                        indicator = null;
                    }
                });

            }
        });

        /* Updates the status indicators colour */
        function update_indicator(col) {
            indicator.style.background = col;
        }
    }
}
