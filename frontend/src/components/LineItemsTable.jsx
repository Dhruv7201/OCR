import React from "react";
import Row from "./Row";

const LineItemsTable = ({
  lineItems,
  handleProductChange,
  handleBatchChange,
  handleMfgChange,
  handleExpChange,
  handleDeleteRow,
  handleAddRow,
  handleSave,
}) => {
  return (
    <div>
      <table className="border">
        <thead>
          <tr>
            <th className="pt-2 pb-2 ps-5 pe-5 border">Product Name</th>
            <th className="pt-2 pb-2 ps-5 pe-5 border">Batch Number</th>
            <th className="pt-2 pb-2 ps-5 pe-5 border">Mfg Date</th>
            <th className="pt-2 pb-2 ps-5 pe-5 border">Exp Date</th>
            <th className="pt-2 pb-2 ps-5 pe-5 border">Delete</th>
          </tr>
        </thead>
        <tbody>
          {lineItems.map((item, index) => (
            <Row
              key={index}
              index={index}
              item={item}
              handleProductChange={handleProductChange}
              handleBatchChange={handleBatchChange}
              handleMfgChange={handleMfgChange}
              handleExpChange={handleExpChange}
              handleDeleteRow={handleDeleteRow}
            />
          ))}
        </tbody>
      </table>
      <div className="mt-2">
        <button className="btn btn-primary me-2" onClick={handleAddRow}>
          Add
        </button>
        <button className="btn btn-primary" onClick={handleSave}>
          Save
        </button>
      </div>
    </div>
  );
};

export default LineItemsTable;
