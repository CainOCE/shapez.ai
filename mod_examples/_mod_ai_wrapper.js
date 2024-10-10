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

    settings: {
        paused: false,
    },
};

BUILDING_LINK_NAME = {
    "belt": "MetaBeltBuilding",
    "miner": "MetaMinerBuilding",
}


class Mod extends shapez.Mod {

    /* Step through Sim Logic */
    step() {
        let root = window.globalRoot;
        let was_paused = this.settings.paused;

        // Guard against undefined root
        if (root && root.time) {
            // Unpause -> Step -> Pause
            this.settings.paused = false;
            root.time.updateRealtimeNow();
            root.time.performTicks(
                root.dynamicTickrate.deltaMs,
                root.gameState.core.boundInternalTick
            );
            root.productionAnalytics.update();
            root.achievementProxy.update();
            this.settings.paused = was_paused;
        } else { console.error("Global root or time is undefined."); }

        return shapez.STOP_PROPAGATION;
    };

    init() {
        console.log("Shapez.ai Module Initialized");
        const mod = this;

        /* Sandbox Mode & Pausing */
        this.modInterface.replaceMethod(shapez.Blueprint, "getCost", () => 0);
        this.modInterface.replaceMethod(
            shapez.HubGoals, "isRewardUnlocked", () => true
        );
        this.modInterface.replaceMethod(shapez.GameHUD, "shouldPauseGame",
            (f) => { return f.call(this) || this.settings.paused; }
        );

        /* Fires when the game has properly initialised */
        this.signals.stateEntered.add(state => {
            if (state instanceof shapez.InGameState) {
                 const checkCameraReady = setInterval(() => {
                    if (window.globalRoot && window.globalRoot.gameState.camera && window.globalRoot.gameState.camera.setDesiredZoom) {
                        ROOT.camera.setDesiredZoom(0.1);
                        clearInterval(checkCameraReady);
                    }
                }, 100);
            }
        });

        /* Executes code under development */
        function test() {
            // Place some various resources as a test.
            let x = 4
            place_resources([
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

        async function train() {
            // Start a training session
            let root = window.globalRoot;
            var gameState = getGameState()
            update_indicator("yellow");

            // Guard against undefined root
            if (root && root.time) {
                // Request a training session on the backend
                var request = await fetch("http://127.0.0.1:5000/train", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(gameState),
                })
                    .then((response) => response.json())
                    .then((response) => {
                        // Response received
                        update_indicator("lightgreen");
                        let state = response["state"]
                        let status = response["status"]
                        let action = response["action"]

                        // Handle the backend state machine
                        if (state == "ONLINE") { return; }
                        else if (state == "EPISODE") { reset(); train(); }
                        else if (state == "PRE_FRAME") { train(); }
                        else if (state == "POST_FRAME") {
                            // Apply action to game, step X, return result
                            for (let i = 0; i < 300; i++) {
                                if (action) { place_entities([action]); };
                                mod.step();
                            }
                            train();
                        }
                        else if (state == "COMPLETE") { return; }
                        else { train(); }
                    })
                    .catch((error) => {
                        console.error("Request failed:", error);
                        update_indicator("red");
                    });
            }
        }

        /* Destroys game and returns to menu state. */
        function reset() {
            window.globalRoot.gameState.stateManager.currentState.goBackToMenu()
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

        /* Places buildings given by the backend as a list solution. */
        function place_entities(entities) {
            const root = window.globalRoot;
            for (let e of entities){
                root.logic.tryPlaceBuilding({
                    origin: new shapez.Vector(e.x, e.y),
                    building: shapez.gMetaBuildingRegistry.findByClass(
                        shapez[`${BUILDING_LINK_NAME[e.type]}`]
                    ),
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
        function tryPlaceResource(resource, x, y) {
            const ROOT = window.globalRoot;
            const COLORS = shapez.COLOR_ITEM_SINGLETONS
            const SHAPES = window.globalRoot.shapeDefinitionMgr

            // Get Chunk by x, y
            let map = ROOT.gameState["core"]["root"]["map"]["chunksById"];
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
                item = ROOT.shapeDefinitionMgr.getShapeItemFromDefinition(
                    shapez.ShapeDefinition.fromShortKey(resource)
                )
            }

            // Place Resource
            chunk.lowerLayer[(x%16+16)%16][(y%16+16)%16] = item;
            return item;
        }

        /* Places resources at the given locations */
        function place_resources(resources) {
            for (let r of resources){
                tryPlaceResource(
                    r.type,
                    r.x, r.y,
                )
            }
        }

        /* Simplifies the notification system. */
        function simpleNotification(msg) {
            window.globalRoot.hud.signals.notification.dispatch(
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
        function getGameState() {
            var gameState = window.globalRoot.gameState;
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

            // 3.  Extract Stored Shapez
            let storage = gameState["core"]["root"]["hubGoals"]["storedShapes"]

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
                storage: storage,
                entities: entities
            };
        }

        /* Sends a communication pulse to the Python Backend */
        async function ping() {
            let root = window.globalRoot;
            // Guard against undefined root
            if (root && root.time) {
                var request = await fetch("http://127.0.0.1:5000/ping", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: "ping",
                })
                    .then((response) => response.json())
                    .then((response) => {
                        if (response == "ONLINE") {
                            // Change indicator to show server comms are live
                            if (indicator.style.background == "lightgreen") {
                                update_indicator("green");
                            } else {
                                update_indicator("lightgreen");
                            }
                        }
                    })
                    .catch((error) => {
                        console.log(error)
                        update_indicator("red");
                });
                // NOTE:  It's super annoying that this generates an error
                //        constantly when it can't connect.  -net in the chrome
                //        devtools filter will hide these messages.
            }
        }
        const intervalId = setInterval(async () => { await ping(); }, 1000);

        /**
         * Sends a gameState obj to the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        async function query() {
            const gameState = getGameState();
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
                    place_entities(data)
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
            }
        });

        /* Updates the status indicators colour */
        function update_indicator(col) {
            indicator.style.background = col;
        }

        /* Use our keybinds */
        const STOP = shapez.STOP_PROPAGATION;
        const ACTIONS = [
            {   /* Test */
                id: "shapez_ai_test_function_trigger",
                keyCode: shapez.keyToKeyCode("F"),
                translation: "trigger_test_function_event",
                modifiers: { shift: true, },
                handler: root => { test(); return STOP; },
            },
            {   /* Pause */
                id: "shapez_ai_pause_trigger",
                keyCode: shapez.keyToKeyCode("P"),
                translation: "trigger_pause_event",
                modifiers: { shift: true, },
                handler: root => {
                    this.settings.paused = !this.settings.paused;
                    return STOP;
                },
            },
            {   /* Step */
                id: "shapez_ai_step_trigger",
                keyCode: shapez.keyToKeyCode("N"),
                translation: "trigger_step_event",
                modifiers: { shift: true, },
                handler: root => { this.step(); return STOP; },
            },
            {   /* Reset */
                id: "shapez_ai_reset_trigger",
                keyCode: shapez.keyToKeyCode("R"),
                translation: "trigger_reset_event",
                modifiers: { shift: true, },
                handler: root => { reset(); return STOP; },
            },
            {   /* Query */
                id: "shapez_ai_query_trigger",
                keyCode: shapez.keyToKeyCode("Q"),
                translation: "trigger_query_event",
                modifiers: { shift: true, },
                handler: root => { query(); return STOP; },
            },
            {   /* Train */
                id: "shapez_ai_training_trigger",
                keyCode: shapez.keyToKeyCode("T"),
                translation: "trigger_training_event",
                modifiers: { shift: true, },
                handler: root => { train(); return STOP; },
            },
        ]
        ACTIONS.forEach(k => this.modInterface.registerIngameKeybinding(k));
    }

}
