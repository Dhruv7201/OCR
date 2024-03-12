import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import Swal from "sweetalert2";

const videoConstraints = {
  width: 440,
  height: 380,
  facingMode: "user",
};

const WebCam = () => {
  const [productDetail, setProductDetail] = useState({
    productName: "",
    batchNumber: "",
  });
  const [lineItems, setLineItems] = useState([]);
  const audioRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const handleAddRow = () => {
    setLineItems((prevLineItems) => [
      ...prevLineItems,
      { productName: "", batchNumber: "" },
    ]);
  };

  const handleDeleteRow = (index) => {
    setLineItems((prevLineItems) =>
      prevLineItems.filter((item, i) => i !== index)
    );
  };

  const handleProductChange = (index, value) => {
    setLineItems((prevLineItems) => {
      const updatedLineItems = [...prevLineItems];
      updatedLineItems[index].productName = value;
      return updatedLineItems;
    });
  };

  const handleBatchChange = (index, value) => {
    setLineItems((prevLineItems) => {
      const updatedLineItems = [...prevLineItems];
      updatedLineItems[index].batchNumber = value;
      return updatedLineItems;
    });
  };

  const handleSave = () => {
    if (lineItems.length === 0) {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Please add atleast one row",
      });
      return;
    }
    if (lineItems.length === 1) {
      if (lineItems[0].productName === "" || lineItems[0].batchNumber === "") {
        Swal.fire({
          icon: "error",
          title: "Oops...",
          text: "Please fill all the rows",
        });
        return;
      }
    }
    for (let i = 0; i < lineItems.length - 1; i++) {
      if (lineItems[i].productName === "" || lineItems[i].batchNumber === "") {
        Swal.fire({
          icon: "error",
          title: "Oops...",
          text: "Please fill all the rows",
        });
        return;
      }
    }
    // remove the last empty row
    lineItems.pop();
    const dataToSave = {
      data: lineItems,
    };
    // Post data to the backend
    axios
      .post("http://0.0.0.0:3001/api/save-data", dataToSave)
      .then((res) => {
        if (res.status === 200) {
          // Clear the lineItems
          setLineItems([]);
          Swal.fire({
            icon: "success",
            title: "Success",
            text: "Data saved successfully",
          });
        }
      })
      .catch((err) => {
        console.error(err);
      });
  };

  useEffect(() => {
    const { productName, batchNumber } = productDetail;
    if (productName || batchNumber) {
      const tableData = {
        productName: productName || "",
        batchNumber: batchNumber || "",
      };

      if (productName !== "") {
        // make beep sound
        audioRef.current.play();
        if (lineItems?.length > 0) {
          const newState = lineItems.map((obj, index) => {
            if (index === lineItems.length - 1) {
              return { ...obj, productName: productName };
            }
            return obj;
          });
          setLineItems(newState);
        } else {
          setLineItems((prevLineItems) => [...prevLineItems, tableData]);
        }
      }
      if (batchNumber !== "") {
        // make beep sound
        audioRef.current.play();
        if (lineItems?.length > 0) {
          const newState = lineItems.map((obj, index) => {
            if (index === lineItems.length - 1) {
              return { ...obj, batchNumber: batchNumber };
            }

            return obj;
          });
          setLineItems(newState);
        } else {
          setLineItems((prevLineItems) => [...prevLineItems, tableData]);
        }
      }
      setProductDetail({ productName: "", batchNumber: "" });
    }
  }, [productDetail]);

  useEffect(() => {
    // add new line if all above are filled
    if (lineItems.length > 0) {
      const lastItem = lineItems[lineItems.length - 1];
      if (lastItem.productName && lastItem.batchNumber) {
        handleAddRow();
      }
    }
  }, [lineItems]);

  const sendFrameToBackend = async () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    canvas.width = videoConstraints.width;
    canvas.height = videoConstraints.height;

    if (videoRef.current) {
      ctx.drawImage(
        videoRef.current,
        0,
        0,
        videoConstraints.width,
        videoConstraints.height
      );
      const imageData = canvas.toDataURL("image/jpeg");

      try {
        const response = await fetch("http://0.0.0.0:3001/api/send-frame", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ frame: imageData }),
        });

        const data = await response.json();
        setProductDetail(data);
      } catch (error) {
        console.error(error);
      }
    }
  };

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: videoConstraints })
      .then((stream) => {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      })
      .catch((error) => {
        console.error("Error accessing webcam:", error);
      });

    const captureInterval = setInterval(sendFrameToBackend, 3000);

    return () => {
      clearInterval(captureInterval);
    };
  }, []);

  return (
    <div className="text-center">
      <audio ref={audioRef}>
        <source src="/beep.mp3" type="audio/mp3" />
      </audio>
      <div className="row">
        <div className="col-md-4">
          <div>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              width={videoConstraints.width}
              height={videoConstraints.height}
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />
          </div>
        </div>
        <div className="col-md-6">
          <div className="p-2">
            <table className="border">
              <thead>
                <tr>
                  <th className="pt-2 pb-2 ps-5 pe-5 border">Product Name</th>
                  <th className="pt-2 pb-2 ps-5 pe-5 border">Batch Number</th>
                  <th className="pt-2 pb-2 ps-5 pe-5 border">Delete</th>
                </tr>
              </thead>
              <tbody>
                {lineItems.map((item, index) => (
                  <tr key={index}>
                    <td className="pt-2 pb-2 ps-5 pe-5 border">
                      <input
                        type="text"
                        value={item.productName}
                        onChange={(e) =>
                          handleProductChange(index, e.target.value)
                        }
                      />
                    </td>
                    <td className="pt-2 pb-2 ps-5 pe-5 border">
                      <input
                        type="text"
                        value={item.batchNumber}
                        onChange={(e) =>
                          handleBatchChange(index, e.target.value)
                        }
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
        </div>
      </div>
    </div>
  );
};

export default WebCam;
