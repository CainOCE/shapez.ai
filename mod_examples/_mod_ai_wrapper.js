// @ts-nocheck
const METADATA = {
    website: "https://tobspr.io",
    author: "fish-obsessed",
    name: "ShapeZ.ai",
    version: "0.0.1",
    id: "shapezai",
    description: "Communicates via REST API with a python backend.",
    minimumGameVersion: ">=1.5.0",
};


class Mod extends shapez.Mod {
    init() {
        console.log("Shapez.ai Module Initialized");


        /* Sandbox Mode */
        this.modInterface.replaceMethod(
            shapez.Blueprint, "getCost",
            function () { return 0; }
        );
        this.modInterface.replaceMethod(
            shapez.HubGoals, "isRewardUnlocked",
            function () { return true; }
        );


        /* Register Custom keybinding */
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_trigger",
            keyCode: shapez.keyToKeyCode("F"),
            translation: "trigger_custom_event",
            modifiers: {
                shift: true,
            },
            handler: root => {
                // Send a move request to the python backend.
                var gameState = getGameState(root)
                backendRequest(root, gameState);

                /* Various Tests */
                // backendRequest(root, "Hello");
                // ryanTest(root);  // Place belt and extractor
                return shapez.STOP_PROPAGATION;
            },
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


        /* Creates a newgame immediately, used in AI model training. */
        function newGame(root) {
            /**
             * Save or quit current game then make a new one wont work as we
             * need the mod laughcher ot stay running ?? or not or do we just
             * need app.py running, can do this way??
             */
            root.gameState.goBackToMenu();
        }


        /* Simplifies the notification system. */
        function simpleNotification(root, msg) {
            // Display a message when called
            root.hud.signals.notification.dispatch(
                msg,
                shapez.enumNotificationType.info
            );
        }


        /* Ryan's Placement Test. */
        function ryanTest(root) {
            simpleNotification(root, "Ryan's Placement Test")
            var belt = shapez.MetaBeltBuilding
            var miner = shapez.MetaMinerBuilding
            var u = tryPlaceSimpleBuilding(root, belt, 3, 4)
            var v = tryPlaceSimpleBuilding(root, miner, 3, 5)
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
            simpleNotification(root, "Gathering gameState...")

            // 1.  Extract Game Seed
            let seed = gameState["core"]["root"]["map"]["seed"];

            // 2.  Extract Level & Goal
            simpleNotification(root, " -> Extracting Goals...")
            let level = gameState["core"]["root"]["hubGoals"]["level"];
            const G = gameState["core"]["root"]["hubGoals"]["currentGoal"];
            let goal = ({
                level: level,
                definition: G.definition,
                required: G.required,
            });
            // TODO:  Defining a goal
            /**
             * Should we judge the model on actual parts per tick, or on a
             * cost vs complexity model.
             */

            // 3.  Extract Map (By Chunks for optimal resource scanning)
            simpleNotification(root, " -> Extracting Map Resources...")
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
            simpleNotification(root, " -> Extracting Entities...");
            const E = gameState["core"]["root"]["entityMgr"]["entities"]
            let entities = E.map(e => {
                let ec = e.components;
                /* Clean the entity description for the backend here. */
                return {
                    uid: e.uid,
                    type:
                        //TODO: Hate it, let's look for an inbuilt getType.
                        !!ec.Hub ? "Hub" : null ||
                            !!ec.Miner ? "Miner" : null ||
                                !!ec.Belt ? "Belt" : null ||
                                    !!ec.UndergroundBelt ? "UndergroundBelt" : null ||
                        "Unknown",
                    x: ec.StaticMapEntity.origin.x,
                    y: ec.StaticMapEntity.origin.y,
                    rotation: ec.StaticMapEntity.rotation,
                    direction:
                        !!ec.Belt
                            ? ec.Belt.direction
                            : null,
                    mode:
                        !!ec.UndergroundBelt
                            ? ec.UndergroundBelt.mode
                            : null,
                };
            });

            // Fin. Return packaged gameState.
            simpleNotification(root, " -> Packaged gameState.")
            return {
                seed: seed,
                map: chunks,
                level: level,
                goal: goal,
                entities: entities
            };
        }


        /**
         * Sends a gameState obj to the python backend.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        async function backendRequest(root, gameState) {
            simpleNotification(root, "Querying AI Model...")
            var request = await fetch("http://127.0.0.1:5000/process", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(gameState),
            })
                .then((response) => response.json())
                .then((data) => {
                    simpleNotification(root, "AI Model Query Complete.")
                    console.log(data);
                })
                .catch((error) => {
                    simpleNotification(root, `Failed to Query Model.`);
                    console.error("Request failed:", error);
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

    }
}
