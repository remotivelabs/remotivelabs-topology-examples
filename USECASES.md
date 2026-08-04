# Use Cases

This document describe a number of different things you typically want to do when working with RemotiveTopology.

This repository includes the following use cases:
- [3D visualization](./usecases/3D.md) - Viewing the vehicle in 3D provides an immersive way to see the current state of the vehicle.
- [Android Cuttlefish](./usecases/ANDROID_CUTTLEFISH.md) - Using Cuttlefish is useful when you are developing applications for your custom Android build or when customizing the Android build.
- [Android Emulator](./usecases/ANDROID_EMULATOR.md) - Using Android Emulator is useful if you are developing Android applications.
- [Behavioral models in python](./usecases/BEHAVIORAL_MODELS.md) - Writing behavioral models in python is a very simple way of creating models for ECUs that don't yet exist.
- [Jupyter notebook](./usecases/JUPYTER.md) - Using RemotiveTopology framework from Jupyter notebook allows you to interact with a running instance and easily create custom user interfaces.
- [Playback signals](./usecases/PLAYBACK_SIGNALS.md) - Using playback of recorded signals can be useful to test longer scenarios.
- [Playback of raw recordings](./usecases/PLAYBACK_RAW.md) - Using playback of raw recordings can be useful when testing user interfaces.
- [Restbus](./usecases/RESTBUS.md) - Use RemotiveTopology to create a simple restbus, i.e. automatically send all frames by one or more ECUs.
- [Test cases in python (behave)](./usecases/TESTCASES_BEHAVE.md) - Using behave to write test cases allows your domain experts to more easily understand the tests that are being run.
- [Test cases in python (pytest)](./usecases/TESTCASES_PYTEST.md) - Using pytest to write test cases is a simple way to express your test cases as code.
- [Traceability with Sphinx-Needs](./usecases/TRACEABILITY_SPHINX.md) - Sphinx-Needs allows you to combine Docs-as-Code with Application Lifecycle Management.

## Related use cases
- Open/Closed loop simulation - In RemotiveTopology both of these are achieved using the playback mechanism, see [Playback signals](./usecases/PLAYBACK_SIGNALS.md) and [Playback of raw recordings](./usecases/PLAYBACK_RAW.md)
