import { Person as PersonIcon } from "@mui/icons-material";

import {
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import React from "react";
import { useState, type FC } from "react";

export type ResourceCopyDialogProps = {
  open: boolean;
  onClose: (value: string[]) => void;
  selectedValue: string;
  resources: ConsParams["resources"];
};

export const ResourceCopyDialog: FC<ResourceCopyDialogProps> = ({
  onClose,
  selectedValue,
  open,
  resources,
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const handleClose = () => {
    onClose(selectedIds);
  };
  const handleCancel = () => {
    onClose([]);
  };

  const onSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((selectedId) => selectedId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  return (
    <Dialog
      onClose={handleCancel}
      open={open}
      sx={{ "& .MuiDialog-paper": { width: "80%", maxHeight: 435 } }}
      maxWidth="xs"
    >
      <DialogTitle>Select Resources to apply constraints to</DialogTitle>
      <DialogContent>
        <List sx={{ pt: 0 }}>
          {resources.map((resource) => (
            <ListItem disableGutters key={resource.id} disablePadding>
              <ListItemButton
                onClick={() => onSelect(resource.id)}
                disabled={selectedValue === resource.id}
              >
                <ListItemIcon>
                  <Checkbox
                    disabled={selectedValue === resource.id}
                    edge="start"
                    checked={
                      selectedValue === resource.id ||
                      selectedIds.includes(resource.id)
                    }
                    tabIndex={-1}
                    disableRipple
                    inputProps={{
                      "aria-labelledby": `checkbox-list-label-${resource.id}`,
                    }}
                  />
                </ListItemIcon>
                <ListItemText
                  id={`checkbox-list-label-${resource.id}`}
                  primary={resource.id}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() =>
            setSelectedIds(resources.map((resource) => resource.id))
          }
        >
          Select All
        </Button>
        <Button autoFocus onClick={handleCancel}>
          Cancel
        </Button>
        <Button onClick={handleClose}>Ok</Button>
      </DialogActions>
    </Dialog>
  );
};
