--liquibase formatted sql

--changeset author:rdube26:create_tables_ira_01
CREATE TABLE ira_gate_type
(
    gate_type_cd    varchar(6)      NOT NULL,
    gate_type_nm    varchar(35)     NOT NULL,
    gate_type_ds    varchar(500)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_02
ALTER TABLE ira_gate_type ADD
    CONSTRAINT ira_gate_type_PK PRIMARY KEY (gate_type_cd);

--changeset author:rdube26:create_tables_ira_03
CREATE TABLE ira_gate
(
    gate_type_cd    varchar(6)     NOT NULL,
    gate_cd         varchar(10)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_04
ALTER TABLE ira_gate ADD
    CONSTRAINT ira_gate_PK PRIMARY KEY (gate_type_cd, gate_cd);

--changeset author:rdube26:create_tables_ira_05
ALTER TABLE ira_gate ADD CONSTRAINT Ref_ira_gate_type1841
    FOREIGN KEY (gate_type_cd)
        REFERENCES ira_gate_type(gate_type_cd);

--changeset author:rdube26:create_tables_ira_06
CREATE TABLE ira_acq_chan
(
    ira_acq_chan_cd          varchar(6)      NOT NULL,
    parnt_ira_acq_chan_cd    varchar(6),
    chan_nm              varchar(30)     NOT NULL,
    creat_user_id        varchar(34)     NOT NULL,
    creat_ts             timestamp(6)    NOT NULL,
    lst_updt_ts          timestamp(6),
    lst_updt_user_id     varchar(34)
);

--changeset author:rdube26:create_tables_ira_07
ALTER TABLE ira_acq_chan ADD
    CONSTRAINT ira_acq_chan_PK PRIMARY KEY (ira_acq_chan_cd);

--changeset author:rdube26:create_tables_ira_08
ALTER TABLE ira_acq_chan ADD CONSTRAINT Ref_ira_cpli_acq_chan1711
    FOREIGN KEY (parnt_ira_acq_chan_cd)
        REFERENCES ira_acq_chan(ira_acq_chan_cd);

--changeset author:rdube26:create_tables_ira_09
CREATE TABLE ira_occpt
(
    ira_occpt_cd        varchar(10)     NOT NULL,
    occpt_nm            varchar(50)     NOT NULL,
    creat_user_id       varchar(34)     NOT NULL,
    creat_ts            timestamp(6)    NOT NULL,
    lst_updt_ts         timestamp(6),
    lst_updt_user_id    varchar(34)
);

--changeset author:rdube26:create_tables_ira_10
ALTER TABLE ira_occpt ADD
    CONSTRAINT ira_occpt_PK PRIMARY KEY (ira_occpt_cd);

--changeset author:rdube26:create_tables_ira_11
CREATE TABLE curr
(
    iso_alpha3_curr_cd    varchar(3)     NOT NULL,
    curr_nm               varchar(40)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_12
ALTER TABLE curr ADD
    CONSTRAINT curr_PK PRIMARY KEY (iso_alpha3_curr_cd);

--changeset author:rdube26:create_tables_ira_13
CREATE TABLE ira_prod_type
(
    ira_prod_type_cd    varchar(10)    NOT NULL,
    prod_type_nm        varchar(30)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_14
ALTER TABLE ira_prod_type ADD
    CONSTRAINT ira_prod_type_PK PRIMARY KEY (ira_prod_type_cd);

--changeset author:rdube26:create_tables_ira_15
CREATE TABLE ira_prod
(
    ira_prod_cd           varchar(10)     NOT NULL,
    prod_nm               varchar(80)     NOT NULL,
    ira_prod_type_cd      varchar(10)     NOT NULL,
    iso_alpha3_curr_cd    varchar(3)      NOT NULL,
    stat_in               boolean         DEFAULT FALSE NOT NULL,
    creat_user_id         varchar(34)     NOT NULL,
    creat_ts              timestamp(6)    NOT NULL,
    lst_updt_ts           timestamp(6),
    lst_updt_user_id      varchar(34)
);

--changeset author:rdube26:create_tables_ira_16
ALTER TABLE ira_prod ADD
    CONSTRAINT ira_prod_PK PRIMARY KEY (ira_prod_cd);

--changeset author:rdube26:create_tables_ira_17
ALTER TABLE ira_prod ADD CONSTRAINT Ref_ira_prod_type1761
    FOREIGN KEY (ira_prod_type_cd)
        REFERENCES ira_prod_type(ira_prod_type_cd);

--changeset author:rdube26:create_tables_ira_18
ALTER TABLE ira_prod ADD CONSTRAINT Ref_curr1771
    FOREIGN KEY (iso_alpha3_curr_cd)
        REFERENCES curr(iso_alpha3_curr_cd);

--changeset author:rdube26:create_tables_ira_19
CREATE TABLE ira_indus_type
(
    ira_indus_type_cd    varchar(10)    NOT NULL,
    indus_type_nm        varchar(70)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_20
ALTER TABLE ira_indus_type ADD
    CONSTRAINT ira_indus_type_PK PRIMARY KEY (ira_indus_type_cd);

--changeset author:rdube26:create_tables_ira_21
CREATE TABLE ira_indus
(
    ira_indus_cd             varchar(10)     NOT NULL,
    indus_nm                 varchar(50)     NOT NULL,
    cash_intensive_bus_in    boolean         NOT NULL,
    ira_indus_type_cd        varchar(10)     NOT NULL,
    creat_user_id            varchar(34)     NOT NULL,
    creat_ts                 timestamp(6)    NOT NULL,
    lst_updt_ts              timestamp(6),
    lst_updt_user_id         varchar(34)
);

--changeset author:rdube26:create_tables_ira_22
ALTER TABLE ira_indus ADD
    CONSTRAINT ira_indus_PK PRIMARY KEY (ira_indus_cd);

--changeset author:rdube26:create_tables_ira_23
ALTER TABLE ira_indus ADD CONSTRAINT Ref_ira_indus_type1741
    FOREIGN KEY (ira_indus_type_cd)
        REFERENCES ira_indus_type(ira_indus_type_cd);

--changeset author:rdube26:create_tables_ira_24
CREATE TABLE ira_geo_div
(
    ira_geo_div_cd    varchar(4)     NOT NULL,
    geo_div_nm        varchar(30)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_25
ALTER TABLE ira_geo_div ADD
    CONSTRAINT ira_geo_div_PK PRIMARY KEY (ira_geo_div_cd);

--changeset author:rdube26:create_tables_ira_26
CREATE TABLE ira_unify_nat_geo_rgn
(
    ira_unify_nat_geo_rgn_cd    varchar(3)      NOT NULL,
    unify_nat_geo_rgn_nm        varchar(100)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_27
ALTER TABLE ira_unify_nat_geo_rgn ADD
    CONSTRAINT ira_unify_nat_geo_rgn_PK PRIMARY KEY (ira_unify_nat_geo_rgn_cd);

--changeset author:rdube26:create_tables_ira_28
CREATE TABLE ira_ctry
(
    ira_ctry_cd                 varchar(2)      NOT NULL,
    ctry_full_nm                varchar(70)     NOT NULL,
    ira_unify_nat_geo_rgn_cd    varchar(3),
    ira_geo_div_cd              varchar(4),
    act_ctry_in                 boolean         NOT NULL,
    strng_reg_envir_in          boolean         NOT NULL,
    creat_user_id               varchar(34)     NOT NULL,
    creat_ts                    timestamp(6)    NOT NULL,
    lst_updt_ts                 timestamp(6),
    lst_updt_user_id            varchar(34)
);

--changeset author:rdube26:create_tables_ira_30
ALTER TABLE ira_ctry ADD
    CONSTRAINT ira_ctry_PK PRIMARY KEY (ira_ctry_cd);

--changeset author:rdube26:create_tables_ira_31
ALTER TABLE ira_ctry ADD CONSTRAINT Ref_ira_unify_nat_geo_rgn1721
    FOREIGN KEY (ira_unify_nat_geo_rgn_cd)
        REFERENCES ira_unify_nat_geo_rgn(ira_unify_nat_geo_rgn_cd);

--changeset author:rdube26:create_tables_ira_32
ALTER TABLE ira_ctry ADD CONSTRAINT Ref_ira_geo_div1731
    FOREIGN KEY (ira_geo_div_cd)
        REFERENCES ira_geo_div(ira_geo_div_cd);

--changeset author:rdube26:create_tables_ira_33
CREATE TABLE ira_pty_type_grp_ctgy
(
    ira_pty_type_grp_ctgy_cd    varchar(6)     NOT NULL,
    pty_type_grp_ctgy_nm        varchar(40)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_34
ALTER TABLE ira_pty_type_grp_ctgy ADD
    CONSTRAINT pty_type_grp_ctgy_PK PRIMARY KEY (ira_pty_type_grp_ctgy_cd);

--changeset author:rdube26:create_tables_ira_35
CREATE TABLE ira_pty_type_grp
(
    ira_type_grp_cd             varchar(6)     NOT NULL,
    pty_type_grp_nm             varchar(40)    NOT NULL,
    ira_pty_type_grp_ctgy_cd    varchar(6)     NOT NULL
);

--changeset author:rdube26:create_tables_ira_36
ALTER TABLE ira_pty_type_grp ADD
    CONSTRAINT ira_pty_type_grp_PK PRIMARY KEY (ira_type_grp_cd);

--changeset author:rdube26:create_tables_ira_37
ALTER TABLE ira_pty_type_grp ADD CONSTRAINT Refira_pty_type_grp_ctgy1751
    FOREIGN KEY (ira_pty_type_grp_ctgy_cd)
        REFERENCES ira_pty_type_grp_ctgy(ira_pty_type_grp_ctgy_cd);


--changeset author:rdube26:create_tables_ira_38
CREATE TABLE ira_pty_type
(
    ira_pty_type_cd           varchar(6)      NOT NULL,
    pty_type_nm               varchar(60)     NOT NULL,
    parnt_ira_pty_type_cd    varchar(6)      NOT NULL,
    ira_type_grp_cd           varchar(6)      NOT NULL,
    creat_user_id             varchar(34)     NOT NULL,
    creat_ts                  timestamp(6)    NOT NULL,
    lst_updt_ts               timestamp(6),
    lst_updt_user_id          varchar(34)
);

--changeset author:rdube26:create_tables_ira_39
ALTER TABLE ira_pty_type ADD
    CONSTRAINT ira_pty_type_PK PRIMARY KEY (ira_pty_type_cd);

--changeset author:rdube26:create_tables_ira_40
ALTER TABLE ira_pty_type ADD CONSTRAINT Ref_ira_pty_type_grp1691
    FOREIGN KEY (ira_type_grp_cd)
        REFERENCES ira_pty_type_grp(ira_type_grp_cd);

--changeset author:rdube26:create_tables_ira_41
ALTER TABLE ira_pty_type ADD CONSTRAINT Ref_ira_pty_type1701
    FOREIGN KEY (parnt_ira_pty_type_cd)
        REFERENCES ira_pty_type(ira_pty_type_cd);

--changeset author:rdube26:create_tables_ira_42
CREATE TABLE ira_sect
(
    gate_type_cd    varchar(6)      NOT NULL,
    ira_sect_cd     varchar(4)      NOT NULL,
    sect_nm         varchar(100)    NOT NULL,
    sect_ord_no     smallint        NOT NULL
)
;

--changeset author:rdube26:create_tables_ira_43
ALTER TABLE ira_sect ADD
    CONSTRAINT ira_sect_PK PRIMARY KEY (gate_type_cd, ira_sect_cd);

--changeset author:rdube26:create_tables_ira_44
ALTER TABLE ira_sect ADD CONSTRAINT Ref_ira_gate_type1861
    FOREIGN KEY (gate_type_cd)
        REFERENCES ira_gate_type(gate_type_cd);

--changeset author:rdube26:create_tables_ira_45
CREATE TABLE ques_risk_ctgy
(
    ques_risk_ctgy_cd    varchar(4)     NOT NULL,
    ques_risk_ctgy_nm    varchar(40)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_46
ALTER TABLE ques_risk_ctgy ADD
    CONSTRAINT ques_risk_ctgy_PK PRIMARY KEY (ques_risk_ctgy_cd);

--changeset author:rdube26:create_tables_ira_47
CREATE TABLE assess_ques
(
    assess_ques_id       smallint         NOT NULL,
    ira_sect_cd          varchar(4)       NOT NULL,
    gate_type_cd         varchar(6)       NOT NULL,
    disp_seq_no          integer          NOT NULL,
    dflt_ans_cd          varchar(3)       NOT NULL,
    ques_risk_ctgy_cd    varchar(4)       NOT NULL,
    assess_ques_tx       varchar(1000)    NOT NULL,
    ques_del_in          boolean          NOT NULL,
    creat_ts             timestamp(6)     NOT NULL,
    creat_user_id        varchar(34)      NOT NULL,
    lst_updt_ts          timestamp(6),
    lst_updt_user_id     varchar(34)
);

--changeset author:rdube26:create_tables_ira_48
ALTER TABLE assess_ques ADD
    CONSTRAINT assess_ques_PK PRIMARY KEY (assess_ques_id);

--changeset author:rdube26:create_tables_ira_49
ALTER TABLE assess_ques ADD CONSTRAINT Ref_ira_sect1661
    FOREIGN KEY (gate_type_cd, ira_sect_cd)
        REFERENCES ira_sect(gate_type_cd, ira_sect_cd);

--changeset author:rdube26:create_tables_ira_50
ALTER TABLE assess_ques ADD CONSTRAINT Ref_ques_risk_ctgy1821
    FOREIGN KEY (ques_risk_ctgy_cd)
        REFERENCES ques_risk_ctgy(ques_risk_ctgy_cd);

--changeset author:rdube26:create_tables_ira_51
CREATE TABLE assess_sta_trk
(
    prod_impl_id     integer         NOT NULL,
    creat_user_id    varchar(34)     NOT NULL,
    creat_ts         timestamp(6)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_52
ALTER TABLE assess_sta_trk ADD
    CONSTRAINT assess_sta_trk_PK PRIMARY KEY (prod_impl_id);

--changeset author:rdube26:create_tables_ira_53
CREATE TABLE assess_sta
(
    assess_sta_cd    varchar(3)     NOT NULL,
    assess_sta_nm    varchar(30)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_54
ALTER TABLE assess_sta ADD
    CONSTRAINT assess_sta_PK PRIMARY KEY (assess_sta_cd);

--changeset author:rdube26:create_tables_ira_55
CREATE TABLE inhrnt_risk_assess
(
    ira_id                      integer         NOT NULL,
    gate_type_cd                varchar(6)      NOT NULL,
    gate_cd                     varchar(10)     NOT NULL,
    assess_sta_cd               varchar(3)      NOT NULL,
    assess_ts                   timestamp(6)    NOT NULL,
    prod_impl_id                integer,
    risk_score_calc_no          integer,
    corruption_risk_score_no    integer,
    creat_user_id               varchar(34)     NOT NULL,
    creat_ts                    timestamp(6)    NOT NULL,
    lst_updt_ts                 timestamp(6),
    lst_updt_user_id            varchar(34)
);

--changeset author:rdube26:create_tables_ira_56
ALTER TABLE inhrnt_risk_assess ADD
    CONSTRAINT inhrnt_risk_assess_PK PRIMARY KEY (ira_id);

--changeset author:rdube26:create_tables_ira_57
ALTER TABLE inhrnt_risk_assess ADD CONSTRAINT Ref_assess_sta1671
    FOREIGN KEY (assess_sta_cd)
        REFERENCES assess_sta(assess_sta_cd);

--changeset author:rdube26:create_tables_ira_58
ALTER TABLE inhrnt_risk_assess ADD CONSTRAINT Ref_assess_sta_trk1681
    FOREIGN KEY (prod_impl_id)
        REFERENCES assess_sta_trk(prod_impl_id);

--changeset author:rdube26:create_tables_ira_59
ALTER TABLE inhrnt_risk_assess ADD CONSTRAINT Ref_ira_gate1831
    FOREIGN KEY (gate_type_cd, gate_cd)
        REFERENCES ira_gate(gate_type_cd, gate_cd);

--changeset author:rdube26:create_tables_ira_60
CREATE TABLE ira_ques_resp
(
    ira_id            integer          NOT NULL,
    assess_ques_id    smallint         NOT NULL,
    assess_ans_cd     varchar(3)       NOT NULL,
    ans_cmnt_tx       varchar(1000)    NOT NULL
);

--changeset author:rdube26:create_tables_ira_61
ALTER TABLE ira_ques_resp ADD
    CONSTRAINT ira_ques_resp_PK PRIMARY KEY (ira_id, assess_ques_id);

--changeset author:rdube26:create_tables_ira_62
ALTER TABLE ira_ques_resp ADD CONSTRAINT Ref_assess_ques1781
    FOREIGN KEY (assess_ques_id)
        REFERENCES assess_ques(assess_ques_id);

--changeset author:rdube26:create_tables_ira_63
ALTER TABLE ira_ques_resp ADD CONSTRAINT Ref_inhrnt_risk_assess1791
    FOREIGN KEY (ira_id)
        REFERENCES inhrnt_risk_assess(ira_id);

--changeset author:rdube26:create_tables_ira_64
CREATE TABLE assess_doc_attach
(
    doc_attach_id         integer         NOT NULL,
    doc_attach_link_tx    text            NOT NULL,
    creat_user_id         varchar(34)     NOT NULL,
    creat_ts              timestamp(6)    NOT NULL,
    ira_id                integer         NOT NULL,
    assess_ques_id        smallint        NOT NULL
);

--changeset author:rdube26:create_tables_ira_65
ALTER TABLE assess_doc_attach ADD
    CONSTRAINT assess_doc_attach_PK PRIMARY KEY (doc_attach_id);

--changeset author:rdube26:create_tables_ira_66
ALTER TABLE assess_doc_attach ADD CONSTRAINT Ref_ira_ques_resp1651
    FOREIGN KEY (ira_id, assess_ques_id)
        REFERENCES ira_ques_resp(ira_id, assess_ques_id);

--changeset author:rdube26:create_tables_ira_67
CREATE TABLE ira_risk_score_ovrrd
(
    gate_type_cd           varchar(6)      NOT NULL,
    gate_cd                varchar(10)     NOT NULL,
    ira_ctry_cd            varchar(2)      NOT NULL,
    assess_sta_cd          varchar(3)      NOT NULL,
    prod_impl_id           integer,
    risk_score_ovrrd_no    integer         NOT NULL,
    creat_user_id          varchar(34)     NOT NULL,
    creat_ts               timestamp(6)    NOT NULL,
    lst_updt_ts            timestamp(6),
    lst_updt_user_id       varchar(34)
);

--changeset author:rdube26:create_tables_ira_68
ALTER TABLE ira_risk_score_ovrrd ADD
    CONSTRAINT ira_risk_score_ovrrd_PK PRIMARY KEY (gate_type_cd, gate_cd, ira_ctry_cd);

--changeset author:rdube26:create_tables_ira_69
ALTER TABLE ira_risk_score_ovrrd ADD CONSTRAINT Ref_assess_sta_trk1801
    FOREIGN KEY (prod_impl_id)
        REFERENCES assess_sta_trk(prod_impl_id);

--changeset author:rdube26:create_tables_ira_70
ALTER TABLE ira_risk_score_ovrrd ADD CONSTRAINT Ref_assess_sta1811
    FOREIGN KEY (assess_sta_cd)
        REFERENCES assess_sta(assess_sta_cd);

--changeset author:rdube26:create_tables_ira_71
ALTER TABLE ira_risk_score_ovrrd ADD CONSTRAINT Ref_ira_gate1851
    FOREIGN KEY (gate_type_cd, gate_cd)
        REFERENCES ira_gate(gate_type_cd, gate_cd);
