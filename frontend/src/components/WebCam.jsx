import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import Swal from "sweetalert2";
import VideoStream from "./VideoStream";
import LineItemsTable from "./LineItemsTable";

const videoConstraints = {
  width: 1080,
  height: 720,
  facingMode: "user",
};

const WebCam = () => {
  const [productDetail, setProductDetail] = useState({
    productName: "",
    batchNumber: "",
    mfgDate: "",
    expDate: "",
  });
  const [lineItems, setLineItems] = useState([]);
  const audioRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const handleAddRow = () => {
    setLineItems((prevLineItems) => [
      ...prevLineItems,
      { productName: "", batchNumber: "", mfgDate: "", expDate: "" },
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

  const handleMfgChange = (index, value) => {
    setLineItems((prevLineItems) => {
      const updatedLineItems = [...prevLineItems];
      updatedLineItems[index].mfgDate = value;
      return updatedLineItems;
    });
  };

  const handleExpChange = (index, value) => {
    setLineItems((prevLineItems) => {
      const updatedLineItems = [...prevLineItems];
      updatedLineItems[index].expDate = value;
      return updatedLineItems;
    });
  };

  const handleSave = () => {
    if (lineItems.length === 0) {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Please add at least one row",
      });
      return;
    }
    if (lineItems.length === 1) {
      if (
        lineItems[0].productName === "" ||
        lineItems[0].batchNumber === "" ||
        lineItems[0].mfgDate === "" ||
        lineItems[0].expDate === ""
      ) {
        Swal.fire({
          icon: "error",
          title: "Oops...",
          text: "Please fill all the rows",
        });
        return;
      }
    }
    for (let i = 0; i < lineItems.length - 1; i++) {
      if (
        lineItems[i].productName === "" ||
        lineItems[i].batchNumber === "" ||
        lineItems[i].mfgDate === "" ||
        lineItems[i].expDate === ""
      ) {
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
      .post("http://192.168.0.194:3001/api/save-data", dataToSave)
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
    const { productName, batchNumber, mfgDate, expDate } = productDetail;
    if (productName || batchNumber || mfgDate || expDate) {
      const tableData = {
        productName: productName || "",
        batchNumber: batchNumber || "",
        mfgDate: mfgDate || "",
        expDate: expDate || "",
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
              return {
                ...obj,
                batchNumber: batchNumber,
                mfgDate: mfgDate,
                expDate: expDate,
              };
            }
            return obj;
          });
          setLineItems(newState);
        } else {
          setLineItems((prevLineItems) => [...prevLineItems, tableData]);
        }
      }
      setProductDetail({
        productName: "",
        batchNumber: "",
        mfgDate: "",
        expDate: "",
      });
    }
  }, [productDetail, lineItems]);

  useEffect(() => {
    if (lineItems.length > 0) {
      const lastItem = lineItems[lineItems.length - 1];
      if (lastItem.productName && lastItem.batchNumber) {
        handleAddRow();
      }
    }
  }, [lineItems]);

  const sendFrameToBackend = useCallback(async () => {
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
        const response = await fetch(
          "http://192.168.0.156:3001/api/send-frame",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ frame: imageData }),
          }
        );

        const data = await response.json();
        console.log(data);
        setProductDetail(data);
      } catch (error) {
        console.error(error);
      }
    }
  }, [videoConstraints]);

  return (
    <div className="text-center">
      <audio ref={audioRef}>
        <source src="/beep.mp3" type="audio/mp3" />
      </audio>
      <div className="row">
        <div className="col-md-4">
          <VideoStream
            videoConstraints={videoConstraints}
            videoRef={videoRef}
            canvasRef={canvasRef}
            sendFrameToBackend={sendFrameToBackend}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-md-6">
          <div className="p-2">
            <LineItemsTable
              lineItems={lineItems}
              handleProductChange={handleProductChange}
              handleBatchChange={handleBatchChange}
              handleMfgChange={handleMfgChange}
              handleExpChange={handleExpChange}
              handleDeleteRow={handleDeleteRow}
              handleAddRow={handleAddRow}
              handleSave={handleSave}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebCam;
