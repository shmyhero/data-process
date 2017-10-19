create database if not exists tradehero;

use tradehero;

--yahoo equity include ajd close.
drop table if exists yahoo_equity;
create table yahoo_equity (
    id int not null auto_increment primary key,
    symbol varchar (32) not null,
    tradeDate date not null,
    openPrice float null,
    highPrice float null,
	lowPrice float null,
	closePrice float null,
	adjClosePrice float null,
	volume float null,
	unique index equity_index (symbol, tradeDate)
);


drop table if exists equity;
create table equity (
    id int not null auto_increment primary key,
    symbol varchar (32) not null,
    tradeTime date not null,
    openPrice float null,
    highPrice float null,
	lowPrice float null,
	lastPrice float null,
	priceChange float null,
	volume float null,
	unique index equity_index (symbol, tradeTime)
);

drop table if exists option_data;
create table option_data (
    id int not null auto_increment primary key,
	underlingSymbol varchar(32) not null,
	tradeTime date not null,
	symbol varchar(32) not null,
	expirationDate date not null,
	the_date date null,
	daysToExpiration int null,
	optionType varchar(32) not null,
	strikePrice float null,
	askprice float null,
	bidDate date null,
	bidPrice float null,
	openPrice float null,
    highPrice float null,
	lowPrice float null,
	lastPrice float null,
	priceChange float null,
	volatility float null,
    theoretical float null,
    delta float null,
    gamma float null,
    rho float null,
    theta float null,
    vega float null,
    openInterest float null,
	volume float null,
	unique index option_index (symbol, tradeTime)
);

alter table option_data add index index_option_underlingSymbol(underlingSymbol);

drop table if exists vix;
create table vix (
    id int not null auto_increment primary key,
    symbol varchar (32) not null,
    lastPrice float null,
	priceChange float null,
    openPrice float null,
    highPrice float null,
	lowPrice float null,
	previousPrice float null,
	volume float null,
    tradeTime varchar(32) not null,
    dailyLastPrice float null,
    dailyPriceChange float null,
    dailyOpenPrice float null,
    dailyHighPrice float null,
    dailyLowPrice float null,
    dailyPreviousPrice float null,
    dailyVolume float null,
    dailyDate1dAgo date null,
    unique index vix_index (symbol, dailyDate1dAgo)
);


drop table if exists nyse_credit;
create table nyse_credit (
    id int not null auto_increment primary key,
    lastDate varchar (32) not null,
    margin_debt float not null,
    cash_accounts int null,
    credit_balance float null,
    the_year int not null,
    the_month int not null,
    unique index nyse_index(lastDate)
);


drop table if exists spy_vix_hedge;
create table spy_vix_hedge (
    id int not null auto_increment primary key,
    trade_date date not null,
    vix_index float not null,
    vix_delta float not null,
    spy_vol float not null,
    spy_price float not null,
    spy_option_delta float not null,
    vix_vol float not null,
    vix_price float not null,
    vxx_delta float not null,
    ratio float not null,
    unique index spy_vix_hedge_index (trade_date)
);


--option ratio view, provide the ratio from stike_price / underling_price
drop view if exists option_ratio_view;
create view option_ratio_view  as (
    select o.underlingSymbol, o.symbol, o.tradeTime, o.optionType, o.volatility, o.expirationDate, o.daysToExpiration, o.lastPrice as option_price, o.delta, o.gamma, o.rho, o.theta, o.vega, o.strikePrice, e.lastPrice as price, o.strikePrice / e.lastPrice as ratio
    from option_data as o,
         equity as e
    where o.underlingSymbol = e.symbol
    and o.tradeTime = e.tradeTime
);

--option volatility view, filter the orv ratio, ATM call from 0.95 to 1.05, OTM put from 0.8 to 0.95, average the volatility for the grouped option symbols
drop view if exists option_vol_view;
create view option_vol_view as (
select orv.underlingSymbol as symbol, orv.tradeTime, orv.optionType, orv.expirationDate, orv.daysToExpiration, orv.price, Avg(orv.volatility) as vol
from option_ratio_view orv
where (orv.ratio >= 0.95 and orv.ratio <= 1.05 and orv.optionType = 'Call')
   or (orv.ratio >= 0.8 and orv.ratio <= 0.95 and orv.optionType = 'Put')
group by orv.underlingSymbol, orv.tradeTime, orv.optionType, orv.expirationDate, orv.daysToExpiration, orv.price
)

--calculate the skew by put_volatility - call_volatility
drop view if exists option_skew_view;
create view option_skew_view as (
select ovv.symbol, ovv.tradeTime, ovv.expirationDate, ovv.daysToExpiration, ovv.price, max(ovv.vol) - min(ovv.vol) as skew
from option_vol_view as ovv
group by ovv.symbol, ovv.expirationDate, ovv.tradeTime, ovv.daysToExpiration, ovv.price
)


--filter the enough liquidity skew by days to expiration from 10 days to 60 days
drop view if exists option_enough_liquidity_skew_view;
create view option_enough_liquidity_skew_view as (
select osv.symbol, osv.tradeTime, osv.price, AVG(osv.skew) as skew
from option_skew_view as osv
where osv.daysToExpiration >= 10
  and osv.daysToExpiration <= 60
group by osv.symbol, osv.tradeTime
)

-- from Wednesday close to next wednesday close.
drop view if exists option_skew_weekly_view;
create view option_skew_weekly_view as (
select symbol, AVG(skew) as skew, FROM_DAYS(TO_DAYS(tradetime) -MOD(TO_DAYS(tradetime) -4, 7)) as balance_date
from  option_enough_liquidity_skew_view group by symbol, FROM_DAYS(TO_DAYS(tradetime) -MOD(TO_DAYS(tradetime) -4, 7))
)


--for yahoo last-date-view
drop view if exists yahoo_equity_last_date_for_month_view;
create view yahoo_equity_last_date_for_month_view as (
select symbol, max(tradeDate) as lastDate, min(tradeDate) as firstDate,  max(highPrice) as highPrice, min(lowPrice) as lowPrice, openPrice
from yahoo_equity
group by year(tradeDate), month(tradeDate), symbol
);

-- for yahoo monthly data, warning: do not use order by in sql, it will makes query slow.
drop view if exists yahoo_equity_monthly_view;
create view yahoo_equity_monthly_view as (
select lv.symbol, lv.firstDate, lv.lastDate, lv.openPrice, lv.highPrice, lv.lowPrice, e.closePrice, e.adjClosePrice,  year(lastDate) as tradeyear, month(lastDate) as trademonth
from yahoo_equity as e,
yahoo_equity_last_date_for_month_view as lv
where e.tradeDate = lv.lastDate
and e.symbol = lv.symbol
);