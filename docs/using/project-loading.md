# Project loading

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
    class g0 selected-mermaid-node
```

After launching PolyChron, users must create or select a **Project** and a **Model** to proceed.

![A screenshot of the welcome screen for the polychron project selection process](../assets/img/screenshots/project-welcome.png)

## Project

In PolyChron, a **Project** is a named collection of **Models** for the same archaeological site, which are stored in the same directory on disk.

The *project* name must be a valid directory name for your filesystem.

The files for the project are stored on-disk within the polychron `projects_directory`, which defaults to `~/Documents/polychron/projects` but can be [configured](./configuration.md).

## Model

A PolyChron **Model** contains all of the data and information for a single chronological model and is a member of a project.

The *model* name must be a valid directory name for your filesystem, and is stored within the *project directory*.

## Creating a new project

From the project selection welcome screen, you can choose to **Create a new project**.
You will then be asked to provide a name for the new project.

![A screenshot of the create project popup window](../assets/img/screenshots/create-project.png)

After a project name is provided, such as `thesis`, you will be asked to provide a *Model* name for a new model within the project.

![A screenshot of the create model popup window](../assets/img/screenshots/create-model.png)

Entering a *model* name and selecting **Submit** will allow you to proceed to [*prior elicitation*](./prior-elicitation.md).

## Selecting an existing project

From the project selection welcome screen, you can choose to **Load existing project**.
You will then be asked to select a project from the list of projects in your `projects_directory`.

![A screenshot of the select project popup window](../assets/img/screenshots/select-project.png)

After selecting a project from the list, and selecting **Load Project**, a list of existing *models** within the *project* will be displayed.

![A screenshot of the select model popup window](../assets/img/screenshots/select-model.png)

You can either:

- select an existing model from the list and press **Load selected model** to proceed to [*prior elicitation*](./prior-elicitation.md);
- or you can create a new model by selecting **Create new model**, provide a *model* name, and press **Submit** to proceed to [*prior elicitation*](./prior-elicitation.md)

## Creating or Selecting a Project and Model from the command line

When launching polychron from the command line, a project name and model name may be provided, which will launch polychron and either select or create the specified project/model.

```bash
polychron --project PROJECT --model MODEL
polychron -p PROJECT -m MODEL
```

## Reopen the project selection window

If you close the project selection window before a model has been selected, it can be re-opened from the main application window using `File > Select Project`.

## Next

When you have created or selected a model, [proceed to *prior elicitation*](./prior-elicitation.md).
