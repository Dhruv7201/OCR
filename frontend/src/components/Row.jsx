import React from "react";

const Row = ({
  index,
  item,
  handleProductChange,
  handleBatchChange,
  handleMfgChange,
  handleExpChange,
  handleDeleteRow,
}) => {
  return (
    <tr>
      <td className="pt-2 pb-2 ps-5 pe-5 border">
        <input
          type="text"
          value={item.productName}
          onChange={(e) => handleProductChange(index, e.target.value)}
        />
      </td>
      <td className="pt-2 pb-2 ps-5 pe-5 border">
        <input
          type="text"
          value={item.batchNumber}
          onChange={(e) => handleBatchChange(index, e.target.value)}
        />
      </td>
      <td className="pt-2 pb-2 ps-5 pe-5 border">
        <input
          type="text"
          value={item.mfgDate}
          onChange={(e) => handleMfgChange(index, e.target.value)}
        />
      </td>
      <td className="pt-2 pb-2 ps-5 pe-5 border">
        <input
          type="text"
          value={item.expDate}
          onChange={(e) => handleExpChange(index, e.target.value)}
        />
      </td>
      <td className="pt-2 pb-2 ps-5 pe-5 border">
        <button
          className="btn btn-danger"
          onClick={() => handleDeleteRow(index)}
        >
          Delete
        </button>
      </td>
    </tr>
  );
};

export default Row;
