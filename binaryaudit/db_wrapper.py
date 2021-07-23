#!/usr/bin/python3

import datetime

import sqlalchemy as db
from sqlalchemy.engine.url import URL
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from envparse import env

class abichecker_db_wrapper:
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

        self.logger.print_debug_logs("Initializing database connection")
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

    def abichecker_initialize_db(self) -> None:
        '''
        '''
        self._initialize_db_connection()

    def is_abichecker_db_connected() -> bool:
        '''
        '''
        if self._session:
            return True
        return False

    def abichecker_get_product_id(self, distroname, derivativename) -> int:
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
