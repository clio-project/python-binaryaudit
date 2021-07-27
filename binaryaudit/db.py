#!/usr/bin/python3

from sqlalchemy.engine.url import URL
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from envparse import env


class wrapper:
    '''
    Wrapper class is a database wrapper to wrap all the calls to
    DB. All the application or the modules should use the public
    api of wrapper class
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
                drivername=env.str('DriverName'),
                host=env.str('Server'),
                database=env.str('Database'),
                username=env.str('User'),
                password=env.str('Password'),
                query={"driver": env.str('Driver')}
        )
        db_engine = create_engine(
                connection_url,
                pool_recycle=self._connection_timeout
        )

        self.logger.note("Initializing database connection")
        metadata = MetaData()
        metadata.reflect(
                db_engine,
                only=[
                    "binaryaudit_checker_baseline_tbl",
                    "binaryaudit_product_tbl",
                    "binaryaudit_abi_checker_transaction_details_tbl",
                    "binaryaudit_transaction_main_tbl"
                ],
        )

        db_map = automap_base(metadata=metadata)
        db_map.prepare()
        self.binaryaudit_checker_baseline_tbl = db_map.classes.binaryaudit_checker_baseline_tbl
        self.binaryaudit_product_tbl = db_map.classes.binaryaudit_product_tbl
        self.binaryaudit_abi_checker_transaction_details_tbl = db_map.classes.binaryaudit_abi_checker_transaction_details_tbl
        self.binaryaudit_transaction_main_tbl = db_map.classes.binaryaudit_transaction_main_tbl

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

    def get_product_id(self, productname, derivativename) -> int:
        '''
        '''
        product_id = 0

        session = self._acquire_session()
        record = (
                session.query(
                    self.binaryaudit_product_tbl).filter_by(
                        ProductName=productname,
                        DerivativeName=derivativename
                    ).one_or_none()
        )

        if record is None:
            prd_record = self.abi_checker_product_tbl(
                    ProductName=productname,
                    DerivativeName=derivativename
            )
            session.add(prd_record)
            self._flush_session(session)

            record = (
                    session.query(
                        self.abi_checker_product_tbl).filter_by(
                            ProductName=productname,
                            DerivativeName=derivativename
                    ).one_or_none())

        self._release_session(session)
        product_id = record.ProductID

        return product_id
