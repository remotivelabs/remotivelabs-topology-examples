IHU Component Requirements
==========================

.. comp_req:: SOME/IP Service Consumption
   :id: COMP_REQ_IHU_SOMEIP
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/ihu/python/ihu/__main__.py
   :satisfies: SYSREQ_MULTI_CHANNEL
   :refines: MDL_IHU

   The Infotainment Head Unit shall consume vehicle signals via
   the SOME/IP service interface provided by the Gateway Module
   and present them to connected applications.

.. comp_req:: IHU Android Emulator Bridge
   :id: COMP_REQ_IHU_ANDROID
   :status: reviewed
   :asil: QM
   :verification_method: test
   :source_doc: remotive_car/models/ihu/python/ihu/broker_to_emulator.py
   :satisfies: SYSREQ_ANDROID
   :refines: MDL_IHU

   The Infotainment Head Unit shall bridge vehicle signals to an
   Android Automotive OS emulator via the broker-to-emulator adapter,
   enabling infotainment application testing with live signal data.
