'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { toast } from 'sonner';

// Define a list of predefined niches. In a real application, this might come from an API.
const predefinedNiches = [
  'Technology',
  'Finance',
  'Healthcare',
  'Retail',
  'Education',
  'Marketing',
];

export function NicheSelectionModal() {
  const { user, updateNiche, loading } = useAuth();
  const [selectedNiche, setSelectedNiche] = useState<string | undefined>(undefined);
  const [isSaving, setIsSaving] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Only open the modal if user is authenticated, not loading, and niche is not set
    if (!loading && user && !user.niche) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [loading, user]);

  const handleSaveNiche = async () => {
    if (!selectedNiche) {
      toast.error('Please select a niche.');
      return;
    }
    setIsSaving(true);
    await updateNiche(selectedNiche);
    setIsSaving(false);
    // Modal will close automatically due to useEffect when user.niche is updated
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Select Your Niche</DialogTitle>
          <DialogDescription>
            To get started, please select the industry niche that best describes your primary focus.
            This helps us tailor your competitive intelligence experience.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <Label htmlFor="niche-selection" className="sr-only">
            Niche
          </Label>
          <RadioGroup
            onValueChange={setSelectedNiche}
            value={selectedNiche}
            className="flex flex-col space-y-2"
          >
            {predefinedNiches.map((nicheOption) => (
              <div key={nicheOption} className="flex items-center space-x-2">
                <RadioGroupItem value={nicheOption} id={nicheOption} />
                <Label htmlFor={nicheOption}>{nicheOption}</Label>
              </div>
            ))}
          </RadioGroup>
        </div>
        <DialogFooter>
          <Button type="submit" onClick={handleSaveNiche} disabled={isSaving || !selectedNiche}>
            {isSaving ? 'Saving...' : 'Save Niche'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
