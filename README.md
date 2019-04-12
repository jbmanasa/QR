# QR

Qualitative reasoning engine that can be used for defined causal model and dependencies.
Outputs a state-graph for an input behavior for an exogenous quantity present in the graph, otherwise a general state-graph can be the output.

The current model is a tap/container/drain system where inflow of the tap is exogenous.

## Output state graphs (PDFs)
The PDFs show the output of the system.
  - Parabolic Inflow
    - parabolic_inflow_3.gv.pdf
    - parabolic_inflow_5.gv.pdf
    - trace_parabolic_inflow_3.gv.pdf
  - Decreasing Inflow
    - decreasing_inflow_3.gv.pdf
    - decreasing_inflow_5.gv.pdf
    - trace_decreasing_inflow_3.gv.pdf
  - General Behavior graph (no inflow specified).
    This is generated based on general natural rules for all quantities as a base model, which is used to create the behavior models above.
    - general_behavior_graph_3.gv.pdf
    - general_behavior_graph_5.gv.pdf
