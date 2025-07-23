# Post-MCMC analysis

```mermaid
graph LR
    g0[Project loading];
    g1[Prior elicitation];
    g2[Posterior inference];
    g3[Post-MCMC analysis];
    g0 --> g1;
    g1 --> g2;
    g2 --> g3;

    classDef selected-mermaid-node fill:#33658a60,stroke:#cc5f00,stroke-width:4px
    class g3 selected-mermaid-node
```

After *posterior inference* is complete and MCMC results are available for a *model*, the *Dating Results* tab can be used for post-MCMC analysis.

The *Dating Results* view includes the chronological DAG which can be used to select contexts and group boundary nodes for subsequent analysis, by right-clicking on the context/group boundary shape.

![A screenshot of the PolyChron Dating Results view for the examples 'thesis' model after calibration has completed](../assets/img/screenshots/dating-results-view.png)

## Posterior Densities

Posterior densities for a selection of contexts or group boundary nodes can plotted by selecting nodes from the chronological graph.

Contexts or group boundaries can be selected by right-clicking on the node and selecting "*Add to results list*".

On clicking the "*Posterior densities*" button, posterior probability density plots for the selected nodes will be displayed.

![A screenshot of the Dating REsults view for the 'thesis' example after posterior densities have been plotted for contexts 1210, 358, 1235, 493 & 925](../assets/img/screenshots/dating-results-view-posterior-densities.png)

The plots are interactive, and can be exported to file using the toolbar at the bottom of the plot area.

![The exported posterior densities for contexts 1210, 358, 1235, 493 & 925 from the 'thesis' example](../assets/img/figures/posterior-densities-export-thesis-1210-358-1235-493-925.png)

## HPD Intervals

*Marginal HPD intervals* for a selection of contexts or group boundary nodes can be displayed in the "*Calendar date range estimates*" table.

Contexts or group boundaries can be selected by right-clicking on the node and selecting "*Add to results list*".

On clicking the "*HPD intervals*" button, you will be prompted for the HPD interval percentage (95% is used as standard). On submission, HPD intervals will be computed and displayed in the "*Calendar date range estimates*" table.

## Time elapsed between contexts or group boundaries

The time elapsed between any two contexts or group boundaries can be examined by:

1. Right click on the first node, selecting "*Get time elapsed*"
2. Right click on the second node, selecting "*Get time elapsed between X and another context*"

The "*Calendar date range estimates*" table will have been updated to include the HPD interval between the two nodes, and the "*Posterior densities*" area will include a plot of the posterior density probability density plot, which can be exported if required.

![A screenshot of the Dating Results tab showing the updated table and posterior densities plot between contexts 1210 and 1235 in the example 'thesis' model](../assets/img/screenshots/dating-results-view-time-between.png)

## Clearing selected contexts, HPD Intervals and Posterior Densities

The "*Clear list*" button can be used to clear the selected nodes, HPD Intervals table and posterior densities plots.
