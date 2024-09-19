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

                // Send a move request to the python backend.
                var gameState = getGameState(root)
                console.dir(gameState)
                // backendRequest(root, "Hello");
                backendRequest(root, gameState);

                return shapez.STOP_PROPAGATION;
            },
        });


        /**
         * Transforms the current gameState to a form readable by our model.
         *
         * @param {type} gameState - Shapez.__
         * @returns {type} None
         */
        function getGameState(root) {
            // TODO: Chunks or map?
            var gameState = root.gameState;
            if (gameState == null) { return; }  // Guard Clause
            simpleNotification(root, "Gathering gameState...")

            // Process State
            if (gameState["key"] == "InGameState") {

                // 1. Extract Entities
                simpleNotification(root, " -> Extracting Entities...");
                const E = gameState["core"]["root"]["entityMgr"]["entities"]
                let entities = E.map(e => ({
                    components: e.components,
                    uid: e.uid
                }));

                // 2. Extract Goals
                simpleNotification(root, " -> Extracting Goals...")
                const G = gameState["core"]["root"]["hubGoals"]["currentGoal"];
                let goal = ({
                    definition: G.definition,
                    required: G.required,
                });

                // 3. Extract Map
                simpleNotification(root, " -> Extracting Map Resources...")
                const M = gameState["core"]["root"]["map"]["chunksById"];
                let resources = Object.values(M).map(m => ({
                    contents: m.contents,
                    lowerLayer: m.lowerLayer,
                    patches: m.patches,
                    tileSpaceRectangle: m.tileSpaceRectangle,
                    tileX: m.tileX,
                    tileY: m.tileY,
                    worldSpaceRectangle: m.worldSpaceRectangle,
                    x: m.x,
                    y: m.y,
                }));

                simpleNotification(root, " -> Packaged gameState.")
                return [entities, resources, goal]
            }
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
                body: JSON.stringify({ game_state: gameState }),
            })
                .then((response) => response.json())
                .then((data) => {
                    simpleNotification(root, "AI Model Query Complete.")
                    console.log(data);
                });
        }

        /* Places a ghost entity at the desired location */
        function addGhostEnitities() { }

        /* Removes a single ghost entity. */
        function removeGhostEntities() { }

        /* Clears all ghost entities on the screen. */
        function clearGhostEntities() { }

        /* Plays a simple animated avatar, ShAIpEZy */
        function playAvatar() { }

    }
}
