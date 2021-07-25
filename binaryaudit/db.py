#!/usr/bin/python3

from sqlalchemy.engine.url import URL
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from envparse import env


class wrapper:
    '''
    '''
    def __init__(self, dbconfig, logger) -> None:
        '''
        '''
        self.logger = logger
        self._connection_timeout = 600
        env.read_envfile(dbconfig)

    def _acquire_session(self):
        '''
        '''
        return self._session()

    def _flush_session(self, session) -> None:
        '''
        '''
        session.commit()

    def _release_session(self, session) -> None:
        '''
        '''
        session.close()

    def _initialize_db_connection(self) -> None:
        '''
        '''
        connection_url = URL(
                drivername="mssql+pyodbc",
                username=env.str('User'),
                password=env.str('Pa'),
                host=env.str('Server'),
                database=env.str('Database'),
                query={"driver": "ODBC Driver 17 for SQL Server"}
        )
        db_engine = create_engine(
                connection_url,
                pool_recycle=self._connection_timeout
        )

        self.logger.info("Initializing database connection")
        metadata = MetaData()
        metadata.reflect(
                db_engine,
                only=[
                    "abi_checker_baseline_tbl",
                    "abi_checker_product_tbl",
                    "abi_checker_transaction_details_tbl",
                    "abi_checker_transaction_main_tbl"
                ],
        )

        db_map = automap_base(metadata=metadata)
        db_map.prepare()
        self.abi_checker_baseline_tbl = db_map.classes.abi_checker_baseline_tbl
        self.abi_checker_product_tbl = db_map.classes.abi_checker_product_tbl
        self.abi_checker_transaction_details_tbl = db_map.classes.abi_checker_transaction_details_tbl
        self.abi_checker_transaction_main_tbl = db_map.classes.abi_checker_transaction_main_tbl

        self._session = sessionmaker(bind=db_engine, expire_on_commit=False)

    def initialize_db(self) -> None:
        '''
        '''
        self._initialize_db_connection()

    def is_db_connected(self) -> bool:
        '''
        '''
        if self._session:
            return True
        return False

    def get_product_id(self, distroname, derivativename) -> int:
        '''
        '''
        product_id = 0

        session = self._acquire_session()
        record = (
                session.query(
                    self.abi_checker_product_tbl).filter_by(
                        DistroName=distroname,
                        DerivativeName=derivativename
                    ).one_or_none()
        )

        if record is None:
            prd_record = self.abi_checker_product_tbl(
                    DistroName=distroname,
                    DerivativeName=derivativename
            )
            session.add(prd_record)
            self._flush_session(session)

            record = (
                    session.query(
                        self.abi_checker_product_tbl).filter_by(
                            DistroName=distroname,
                            DerivativeName=derivativename
                    ).one_or_none())

        self._release_session(session)
        product_id = record.ProductID

        return product_id


class orchestrator:
    '''
    ABI checker orchestrator class for the trigger the abi checker functionality.
    '''

    def __init__(self, distroname, derivative, build_id, telemetery, logger):
        '''
        '''
        self.logger = logger
        self.distroname = distroname
        self.derivative = derivative
        self.build_id = build_id
        self.product_id = 0
        self.enable_telemetry = telemetery

        # Instantiate the db connection to upload results to DB
        if self.enable_telemetry == 'y':
            self.db_conn = wrapper("db_config", self.logger)
            self.db_conn.initialize_db()

    def initalize_product_id(self) -> None:
        '''
        '''
        if self.db_conn.is_db_connected:
            product_id = self.db_conn.get_product_id(
                    self.distroname,
                    self.derivative
            )
            self.logger.info("Product_id: %s" % product_id)
        else:
            self.logger.debug("Not connected")
