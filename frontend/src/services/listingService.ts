import api from "./api";
import type { Listing } from "@/types/listing";

export default {
  getAll(params: any) {
    return api.get("/listings", { params });
  },
  get(id: string) {
    return api.get(`/listings/${id}`);
  },
  create(listing: Partial<Listing>) {
    return api.post("/listings", listing);
  },
  update(id: string, listing: Partial<Listing>) {
    return api.put(`/listings/${id}`, listing);
  },
  delete(id: string) {
    return api.delete(`/listings/${id}`);
  },
  uploadImage(id: string, file: File) {
    // 1. Get presigned URL
    return api
      .post(`/listings/${id}/images/presigned-url`, {
        file_name: file.name,
        content_type: file.type,
      })
      .then(async (response) => {
        const { upload_url, s3_key } = response.data;

        // 2. Upload to S3
        await fetch(upload_url, {
          method: "PUT",
          body: file,
          headers: {
            "Content-Type": file.type,
          },
        });

        // 3. Confirm upload
        return api.post(`/listings/${id}/images/confirm`, { s3_key });
      });
  },
};
