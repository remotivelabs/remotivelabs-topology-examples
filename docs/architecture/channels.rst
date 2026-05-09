Communication Channels
======================

.. channel:: Driver CAN Bus
   :id: CH_DRIVER_CAN0
   :status: reviewed
   :channel_name: DriverCan0
   :protocol: CAN
   :signal_database: platform/databases/driver_can.dbc
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_BCM; ECU_SCCM; ECU_TCU

   Primary CAN bus carrying driver input signals from the
   steering column to the body control module.

.. channel:: Body CAN Bus
   :id: CH_BODY_CAN0
   :status: reviewed
   :channel_name: BodyCan0
   :protocol: CAN
   :signal_database: platform/databases/body_can.dbc
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_BCM; ECU_FLCM; ECU_RLCM; ECU_DIM; ECU_GWM; ECU_HVAC; ECU_PAM

   CAN bus carrying body electronics signals including
   lighting commands and comfort system status.

.. channel:: Chassis CAN Bus
   :id: CH_CHASSIS_CAN0
   :status: reviewed
   :channel_name: ChassisCan0
   :protocol: CAN
   :signal_database: platform/databases/chassis_can.dbc
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_ABS; ECU_GWM

   CAN bus carrying chassis and powertrain signals
   including vehicle speed and braking data.

.. channel:: Rear Light LIN Bus
   :id: CH_REAR_LIGHT_LIN
   :status: reviewed
   :channel_name: RearLightLIN
   :protocol: LIN
   :source_doc: remotive_car/platform/remotive-car.platform.yaml
   :connects_to: ECU_RLCM; ECU_RL; ECU_DEVS2

   LIN bus connecting the rear light control module to
   the physical rear light unit.

.. channel:: SOME/IP Network
   :id: CH_SOMEIP
   :status: reviewed
   :channel_name: SOMEIP
   :protocol: SOME/IP
   :source_doc: remotive_car/platform/someip.platform.yaml
   :connects_to: ECU_GWM; ECU_IHU

   Service-oriented middleware connecting the gateway
   module to the infotainment head unit.
