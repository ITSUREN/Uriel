// src/hooks/useIndexProgress.js
import { useState, useEffect, useRef } from "react";
import { getIndexStatus } from "../services/api";

const POLL_INTERVAL_MS = 1200;

export function useIndexProgress({ enabled = true } = {}) {
  const [status, setStatus] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false; // guards against setState after unmount/disable

    function poll() {
      getIndexStatus()
        .then((res) => {
          if (cancelled) return;
          setStatus(res.data);
          const running = res.data.state === "running";
          timerRef.current = setTimeout(poll, running ? POLL_INTERVAL_MS : POLL_INTERVAL_MS * 3);
        })
        .catch(() => {
          // Backend hiccup mid-poll shouldn't kill the loop -- just retry.
          if (cancelled) return;
          timerRef.current = setTimeout(poll, POLL_INTERVAL_MS * 3);
        });
    }

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timerRef.current);
    };
  }, [enabled]);

  return status; // null until first response arrives
}