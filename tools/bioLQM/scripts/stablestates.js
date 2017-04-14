stabletool = new org.colomoto.logicalmodel.tool.stablestate.StableStateTool();

if (gs.args.length == 0) {
    print("No model specified\n");
    quit();
}

model = lm.loadModel(gs.args[0]);
stabletool.run(model);

