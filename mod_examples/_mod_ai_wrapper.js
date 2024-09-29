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

const buildings = {
    "Belt": shapez.MetaBeltBuilding,
    "Miner": shapez.MetaMinerBuilding,
}

class Mod extends shapez.Mod {

    init() {
        console.log("Shapez.ai Module Initialized");

        /* Sandbox Mode */
        this.modInterface.replaceMethod(shapez.Blueprint, "getCost", () => 0);
        this.modInterface.replaceMethod(
            shapez.HubGoals, "isRewardUnlocked", () => true
        );

        /* Register Custom keybindings */
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_reset_trigger",
            keyCode: shapez.keyToKeyCode("R"),
            translation: "trigger_reset_event",
            modifiers: { shift: true, },
            handler: root => {
                resetGame(root)
                return shapez.STOP_PROPAGATION;
            },
        });
        this.modInterface.registerIngameKeybinding({
            id: "shapez_ai_custom_trigger",
            keyCode: shapez.keyToKeyCode("F"),
            translation: "trigger_custom_event",
            modifiers: { shift: true, },
            handler: root => {
                // Send a move request to the python backend.
                backendRequest(root, getGameState(root));
                return shapez.STOP_PROPAGATION;
            },
        });


        /* Destroys all non-hub map entities and clears progression. */
        function resetGame(root) {
            // Remove all Entities
            const E = root.gameState["core"]["root"]["entityMgr"]["entities"]
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
         * @param {number} y offsetparam0.rotation
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
                variant: "default",
                rotationVariant: rotation == 0 ? 0 : 1,
            });
        }

        /** Places buildings given by the backend as a list solution.
         *
         */
        function place_entities(root, entities) {
            for (let e of entities){
                tryPlaceSimpleBuilding(
                    root,
                    buildings[e.type],
                    e.x, e.y,
                    e.rotation
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
            // TODO:  Defining a goal
            /**
             * Should we judge the model on actual parts per tick, or on a
             * cost vs complexity model.
             */

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
            let entities = E.map(e => {
                let ec = e.components;

                // Define Entity by Attached Components
                const getType = (ec) => {
                    // Define Entity by Attached Components
                    if (ec.Miner) return "miner";
                    if (ec.Belt) return "belt";
                    if (ec.UndergroundBelt) {
                        type = ec.UndergroundBelt.mode;
                        tier = ec.UndergroundBelt.tier;
                        return `${type}${tier}`;
                    }
                    if (ec.ItemProcessor) return ec.ItemProcessor.type;
                    if (ec.Storage) return "storage";

                    // TODO Balancers are fun
                    // console.log(ec)
                    return "Unknown";
                };

                /* Clean the entity description for the backend here. */
                return {
                    uid: e.uid,
                    type: getType(ec),
                    x: ec.StaticMapEntity.origin.x,
                    y: ec.StaticMapEntity.origin.y,
                    rotation: ec.StaticMapEntity.rotation,
                    direction: !!ec.Belt ? ec.Belt.direction : null,
                    mode: !!ec.UndergroundBelt ? ec.UndergroundBelt.mode : null,
                };
            });

            // Fin. Return packaged gameState.
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
            var request = await fetch("http://127.0.0.1:5000/query_model", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(gameState),
            })
                .then((response) => response.json())
                .then((data) => {
                    simpleNotification(root, "AI Model Query Complete.")
                    console.log("Return Data:");
                    console.dir(data)
                    place_entities(root, data)
                })
                .catch((error) => {
                    simpleNotification(root, `Failed to Query Model.`);
                    console.error("Request failed:", error);
                });
        }


    }
}
