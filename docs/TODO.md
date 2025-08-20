# Ibiza Development TODO

## Research
- [ ] Enums purpose and use cases
- [ ] Vartypes for schemas & constants

## Data Loading
- [x] ~~Need to merge futures meta into contract meta and use single metadata dataframe~~
- [x] ~~Need to finalize datareader for parquet, csv, and ods~~

## Future Objects

### Future Instruments Objects
- [ ] `FutureInstrument`
- [ ] `FutureMetaData`
- [ ] `FutureInstrumentWithMetaData` (Instrument + MetaData)
- [ ] `ListOfFutureInstrumentsWithMetaData`

### Contract Objects
- [ ] `FutureContract` (Dates + Instrument)
- [ ] Contract date components:
  - [ ] `ExpiryDate`
  - [ ] `ContractDate`
  - [ ] `LastTradableDate`
  - [ ] **OPTIONAL**: `ParametersForFutureContract`
- [ ] `ListOfFutureContracts`
- [ ] `DictOfFutureContractPrices`
- [ ] `DictOfNamedFutureContractPrices`

### Roll Objects
- [ ] `RollCalendar` (DictOfFutureContractPrices + RollParameters)
- [ ] `RollParameters`
- [ ] `ContractDateWithRollParameters` (RollParameters + ContractDate)

---

*This TODO list tracks the development of domain objects and data structures for the Ibiza futures data management system.*