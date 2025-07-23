# ![PolyChron](assets/img/logo.png)

PolyChron is a GUI application designed to facilitate the analysis and archiving of archaeological dating evidence. 
It supports the management of both relative and absolute dating evidence, enabling users to build multiple chronological models within a Bayesian modelling framework.

Key features include:

- Graph-theoretic representations of stratigraphic sequences, which users can explore and edit via an intuitive point-and-click interface.

- The ability to input prior knowledge, such as:

    - Groupings of archaeological contexts

    - Identification of residual or intrusive samples

    - Relationships between different groups

Using this information, PolyChron constructs a hierarchical Bayesian model and uses an MCMC (Markov Chain Monte Carlo) algorithm to estimate the posterior calendar ages of samples.

All outputs, including raw digital data (as input by the user), model representations, results, and supplementary notes are saved locally.
This ensures the full site archive is preserved for future use and long-term archiving with the Archaeology Data Service.

PolyChron is available from [github.com/bryonymoody/PolyChron]({{ config.repo_url }})

## License

PolyChron is released under the [GPLv3 license]({{ config.repo_url }}/blob/main/LICENSE)

## Documentation

This documentation is for `polychron` `v{{ polychron_version_public }}` {% if git.status %}([`{{ git.short_commit }}`]({{ config.repo_url }}/blob/{{ git.commit }})){% endif %}.

If you require version specific documentation, please see the [readme]({{ config.repo_url}}/blob/main/README.md) for instructions on building documentation from source.
