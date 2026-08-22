from datetime import date
from decimal import Decimal
from pathlib import Path

from app.services.cdsl.cas_parser import CDSLCASParser


CAS_PDF = (
    Path(__file__).parent
    / "fixtures"
    / "cdsl"
    / "monthly_cas.pdf"
)


def test_parse_statement_period():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    assert result.statement_start_date == date(
        2026,
        7,
        1,
    )

    assert result.statement_end_date == date(
        2026,
        7,
        31,
    )


def test_parse_total_portfolio_value():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    assert result.portfolio_value == Decimal(
        "36580.99"
    )


def test_parse_all_holdings():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    assert len(result.holdings) == 6

    assert {
        holding.isin
        for holding in result.holdings
    } == {
        "INF247L01AP3",
        "INF277KA1943",
        "INF843K01AO4",
        "INF179KC1FB2",
        "INF179KA1RW5",
        "INF205K013T3",
    }


def test_parse_groww_holding():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    holdings = {
        holding.isin: holding
        for holding in result.holdings
    }

    holding = holdings["INF247L01AP3"]

    assert holding.units == Decimal(
        "3.000"
    )

    assert holding.market_price == Decimal(
        "305.1800"
    )

    assert holding.market_value == Decimal(
        "915.54"
    )

    assert "MOTILAL OSWAL" in (
        holding.security_name.upper()
    )


def test_parse_tata_silver_holding():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    holdings = {
        holding.isin: holding
        for holding in result.holdings
    }

    holding = holdings["INF277KA1943"]

    assert holding.units == Decimal(
        "70.872"
    )

    assert holding.market_price == Decimal(
        "28.3660"
    )

    assert holding.market_value == Decimal(
        "2010.36"
    )

    assert "TATA SILVER ETF" in (
        holding.security_name.upper()
    )


def test_parse_hdfc_small_cap_holding():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    holdings = {
        holding.isin: holding
        for holding in result.holdings
    }

    holding = holdings["INF179KA1RW5"]

    assert holding.units == Decimal(
        "91.815"
    )

    assert holding.market_price == Decimal(
        "160.0460"
    )

    assert holding.market_value == Decimal(
        "14694.62"
    )

    assert "HDFC SMALL CAP FUND" in (
        holding.security_name.upper()
    )


def test_parse_all_holding_values():

    parser = CDSLCASParser()

    result = parser.parse(
        CAS_PDF,
    )

    holdings = {
        holding.isin: holding
        for holding in result.holdings
    }

    expected_values = {
        "INF247L01AP3": Decimal("915.54"),
        "INF277KA1943": Decimal("2010.36"),
        "INF843K01AO4": Decimal("13308.10"),
        "INF179KC1FB2": Decimal("5050.08"),
        "INF179KA1RW5": Decimal("14694.62"),
        "INF205K013T3": Decimal("602.29"),
    }

    for isin, expected_value in expected_values.items():

        assert holdings[isin].market_value == (
            expected_value
        )