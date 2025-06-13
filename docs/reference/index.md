# Developer Reference

> [!Warning]
>
> `PolyChron` is primarily intended to be used as a GUI application, rather than a python library.
>
> The reference documentation is intended to support development and pre-1.0 breaking changes to the API may occur at any time.

PolyChron is a `tkinter` GUI application, which has been structured following a Model-View-Persenter structure.

- Model classes are contained within the `models` submodule, and contain the underlying data and methods to manipulate the data.
- View classes contain the `tkinter` GUI code and are contained within the `views` submodule. They are implemented as *passive views* to simplify testing via mocking.
- Presenter clasess conect the underlying data (Model) with the GUI (View), and are located within the `presenters` submodule. Presenters typically have a corresponding View class, while the Model class is likely shared with other Presenters.

The `GUIApp` module is the main class which initialses the Models, Views and Presenters, and starts the render loop.
