import json
from pydantic import (
    BaseModel,
    Field,
    root_validator,
    validator,
    SecretStr,
)
from typing import Optional, Dict, Any


class ProcessObj(BaseModel):
    """Process Object receive from `P_PRCS_OBJ`"""

    @classmethod
    def get_field_names(cls, alias=False):
        return list(cls.schema(alias).get("properties").keys())

    # Main
    strem_nm: str = Field(..., alias='STREM_NM')
    chk_strem_f: int = Field(..., alias='CHK_STREM_F')
    prcs_grp: str = Field(..., alias='PRCS_GRP')
    prcs_typ: int = Field(..., alias='PRCS_TYP')
    prcs_load_typ: str = Field(..., alias='PRCS_LOAD_TYP')

    # Source information
    asat_dt: str = Field(..., alias='ASAT_DT')
    prv_asat_dt: str = Field(..., alias='PRV_ASAT_DT')
    calc_asat_dt: str = Field(..., alias='CALC_ASAT_DT')

    bus_date_field: Optional[str] = Field(default=None, alias='BUS_DATE_FIELD')
    chk_pk_cols: Optional[str] = Field(default=None, alias='CHK_PK_COLS')
    dist_typ: Optional[str] = Field(default=None, alias='DIST_TYP')
    tbl_strctr_opt: Optional[str] = Field(default=None, alias='TBL_STRCTR_OPT')
    hash_col: Optional[str] = Field(default=None, alias='HASH_COL')
    cus_qry: Optional[str] = Field(default=None, alias='CUS_QRY')
    skip_chk_f: Optional[str] = Field(default=None, alias='SKIP_CHK_F')

    fi_id: Optional[str] = Field(default=None, alias='FI_ID')

    # Source Connection
    sys_nm: Optional[str] = Field(default=None, alias='SYS_NM')
    src_schm_nm: Optional[str] = Field(default='demo/job/', alias='SRC_SCHM_NM')
    src_tbl: Optional[str] = Field(default=None, alias='SRC_TBL')
    cnct_nm: Optional[str] = Field(default=None, alias='CNCT_NM')
    service: Optional[str] = Field(default=None, alias='SERVICE')
    ir: Optional[str] = Field(default=None, alias='IR')
    server_nm: Optional[str] = Field(default=None, alias='SERVER_NM')
    db_nm: Optional[str] = Field(default=None, alias='DB_NM')
    user_nm: Optional[str] = Field(default=None, alias='USER_NM')
    secret_nm: Optional[SecretStr] = Field(default=None, alias='SECRET_NM')

    cntnr: Optional[str] = Field(default=None, alias='CNTNR')
    pth: Optional[str] = Field(default=None, alias='PTH')

    # Target Connection
    tgt_sys_nm: Optional[str] = Field(default=None, alias='TGT_SYS_NM')
    tgt_schm_nm: Optional[str] = Field(default=None, alias='TGT_SCHM_NM')
    tgt_tbl: Optional[str] = Field(default=None, alias='TGT_TBL')
    tgt_cntn_nm: Optional[str] = Field(default=None, alias='TGT_CNTN_NM')
    tgt_ir: Optional[str] = Field(default=None, alias='TGT_IR')
    tgt_service: Optional[str] = Field(default=None, alias='TGT_SERVICE')
    tgt_server_nm: Optional[str] = Field(default=None, alias='TGT_SERVER_NM')
    tgt_db_nm: Optional[str] = Field(default=None, alias='TGT_DB_NM')
    tgt_user_nm: Optional[str] = Field(default=None, alias='TGT_USER_NM')
    tgt_secret_nm: Optional[SecretStr] = Field(default=None, alias='TGT_SECRET_NM')

    tgt_cntnr: Optional[str] = Field(default=None, alias='TGT_CNTNR')
    tgt_pth: Optional[str] = Field(default=None, alias='TGT_PTH')

    # Other Parameters from `CNTL_CFG_PRCS_SPLMNT`
    others: dict = Field(default_factory=dict)

    @root_validator(pre=True)
    @classmethod
    def prepare_values(cls, values):
        _exist_others: dict = values.pop('others', {})
        _others: dict = {
            _: values[_]
            for _ in values
            if (
                    _ != 'others' and
                    _ not in cls.get_field_names(alias=True) and
                    _ not in cls.get_field_names(alias=False)
            )
        }
        return {
            'others': _others | _exist_others,
            **values,
        }

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None
        }


class ADFObject(BaseModel):
    """Process Object receive form ADF"""
    p_prcs_obj: ProcessObj = Field(..., alias='P_PRCS_OBJ')
    p_ld_id: str = Field(default="", alias='P_LD_ID')

    @root_validator(pre=True)
    @classmethod
    def prepare_values(cls, values):
        return values

    @validator('p_prcs_obj', pre=True)
    @classmethod
    def prepare_prcs_obj(cls, value):
        if isinstance(value, str):
            value: Dict[str, Any] = json.loads(value)
        return value

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None
        }
